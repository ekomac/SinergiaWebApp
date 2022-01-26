from django.http.response import JsonResponse
import unidecode
from typing import List, Tuple
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from account.decorators import allowed_users, allowed_users_in_class_view
from account.forms import AccountAuthenticationForm, PasswordResetForm
from envios.models import Envio
from utils.views import CompleteListView
from .models import Account


DEFAULT_RESULTS_PER_PAGE = 30


def logout_view(request):
    logout(request)
    return redirect('login')


def login_view(request):
    context = {}
    form = AccountAuthenticationForm()
    if request.user.is_authenticated:
        if request.user.groups.exists() \
                and request.user.groups.filter(
                name__in=["Admins", "Clients"]).exists():
            return redirect('admin-home')
        else:
            return redirect('index')

    if request.POST:
        form = AccountAuthenticationForm(
            request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(
                email=email, password=password)

            if user:
                login(request, user)

                next_url = 'admin-home'
                if user.groups.exists():
                    if user.groups.filter(
                            name__in=['Admins', 'Clients']).exists():
                        next_url = 'admin-home'
                    else:
                        next_url = 'index'
                spec_url = request.GET.get(
                    'next', None)
                if spec_url:
                    return redirect(spec_url)
                return redirect(next_url)

    context['login_form'] = form

    return render(
        request, 'account/login.html', context)


def forced_reset_password_view(request):
    return render(
        request,
        'registration/forced_password_reset.html',
        {})


def edit_account_view(request):
    context = {}
    return render(
        request, 'account/edit.html', context)


class EmployeesListView(CompleteListView, LoginRequiredMixin):

    template_name = 'account/employees_files/list.html'
    model = Account
    decoders = (
        {
            'key': 'is_active',
            'filter': 'is_active',
            'function': lambda x: True if x == 'true' else False,
            'context': lambda x: x,
        },
        {
            'key': 'has_envios',
            'filter': 'envios_carried_by__isnull',
            'function': lambda x: True if x == 'false' else False,
            'context': lambda x: x,
        },
    )
    query_keywords = (
        'username__icontains', 'first_name__icontains', 'last_name__icontains',
        'client__name__icontains', 'email__icontains', 'dni__icontains',
        'phone__icontains', 'address__icontains',)

    selected_tab = 'files-tab'

    @allowed_users_in_class_view(roles=["Admins"])
    def get(self, request):
        return super(EmployeesListView, self).get(request)

    def get_model_queryset(self):
        queryset = super().get_model_queryset()
        filters = {
            'groups__name__in': ['Admins', 'Level 1', 'Level 2'],
            'is_active': True,
        }
        return queryset.filter(**filters)

    def queryset_map_callable(self, obj):
        envios_carried = Envio.objects.filter(
            carrier=obj,
            status=Envio.STATUS_MOVING
        ).count()
        return (obj, envios_carried)

    def get_verbose_name_plural(self):
        return "Empleados/as"


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def employees_list_view_old(request):

    context = {}

    # Search
    query = ""
    if request.method == "GET":
        query = request.GET.get("query_by", "")
        if query:
            context["query_by"] = str(query)

        order_by = request.GET.get("order_by", 'last_name')
        if order_by:
            order_by = str(order_by)
            context["order_by"] = order_by
            if '_desc' in order_by:
                order_by = "-" + order_by[:-5]

        results_per_page = request.GET.get(
            "results_per_page", DEFAULT_RESULTS_PER_PAGE)
        context['results_per_page'] = str(results_per_page)

        # Filter employees
        employees = get_employees_queryset(query, order_by)

        # Pagination
        page = request.GET.get('page', 1)
        employees_paginator = Paginator(employees, results_per_page)
        try:
            employees = employees_paginator.page(page)
        except PageNotAnInteger:
            employees = employees_paginator.page(results_per_page)
        except EmptyPage:
            employees = employees_paginator.page(employees_paginator.num_pages)

        context['employees'] = employees
        context['totalEmployees'] = len(employees)
        context['selected_tab'] = 'files-tab'
    return render(request, 'account/employees_files/list_old.html', context)


def get_employees_queryset(
        query: str = None, order_by_key: str = 'name',
) -> List[Account]:
    """Get all employees that match provided query, if any. If none is given,
    returns all employees. Also, performs the query in the specified
    order_by_key.

    Args:
        query (str, optional): words to match the query. Defaults to empyt str.
        order_by_key (str, optional): to perform ordery by. Defaults to 'name'.

    Returns:
        List[Account]: a list containing account employees which match at least
        one query.
    """
    query = unidecode.unidecode(
        query) if query else ""
    return list(map(map_employees_to_tuple, list(
        Account.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(dni__icontains=query)
        ).order_by(order_by_key).distinct())))


def map_employees_to_tuple(account: Account) -> Tuple[Account, int]:
    """
    Maps an employee account to a tuple containing the account and an int
    representing que amount of envios being carring by the employee.

    Args:
        account (Account): the account to be mapped.

    Returns:
        Tuple[Account, int]: the mapped account, the int with the no. of
        envios being carried.
    """
    carrying = Envio.objects.filter(
        carrier__id=account.pk, status=Envio.STATUS_MOVING).count()
    return (account, carrying)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def employee_create_view(request):
    return render(request, '', {})


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def employee_detail_view(request, pk):
    context = {}
    employee = get_object_or_404(Account, pk=pk)
    context['employee'] = employee
    context['selected_tab'] = 'files-tab'
    context['envios'] = Envio.objects.filter(
        carrier__id=employee.pk, status__in=[Envio.STATUS_MOVING]
    ).order_by('-date_created')
    return render(request, 'account/employees_files/detail.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def employee_edit_view(request, pk):
    return render(request, 'account/employees_files/edit.html', {})


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def employee_delete_view(request, pk):
    return render(request, 'account/employees_files/delete.html', {})


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "Clients"])
def reset_password_for_employee(request, pk):
    if request.is_ajax and request.method == "POST":
        # get the form data
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(
                Account, pk=pk)
            user.has_to_reset_password = True
            user.save()
            # serialize in new friend object in json
            # ser_instance = serializers.serialize('json', [ids, ])
            # send to client side.
            return JsonResponse({"user_id": pk}, status=200)
        else:
            return JsonResponse({"error": form.errors}, status=400)

    # some error occured
    return JsonResponse({"error": "Unexpected error"}, status=400)
