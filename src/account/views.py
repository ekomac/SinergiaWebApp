# Python
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
from datetime import datetime
import unidecode
from typing import List, Tuple

# Django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect

# Project
from account.decorators import allowed_users, allowed_users_in_class_view
from account.forms import (
    AccountAuthenticationForm,
    CreateAccountForm,
    PasswordResetForm,
    UpdateAccountForm
)
from account.models import Account
from clients.models import Client
from envios.models import Envio
from utils.alerts.alert import ToastAlert
from utils.alerts.views import (
    create_alert_and_redirect, update_alert_and_redirect)
from utils.forms import CheckPasswordForm
from utils.views import CompleteListView, DeleteObjectsUtil, truncate_start


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

            if not user.is_active:
                return HttpResponse("Usuario inactivo.")

            if user:
                login(request, user)

                next_url = 'admin-home'
                if user.groups.exists():
                    if user.groups.filter(
                            name__in=['Admins', ]).exists():
                        next_url = 'admin-home'
                    elif user.groups.filter(
                            name__in=['Clients', ]).exists():
                        return redirect(reverse('clients_only:index'))
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


def edit_account_view(request):
    context = {}
    return render(
        request, 'account/edit.html', context)


class EmployeesListView(CompleteListView, LoginRequiredMixin):

    template_name = 'account/employees_files/list.html'
    model = Account
    decoders = (
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

    selected_tab = 'accounts-tab'

    @allowed_users_in_class_view(roles=["Admins"])
    def get(self, request):
        return super(EmployeesListView, self).get(request)

    def get_model_queryset(self):
        queryset = super().get_model_queryset()
        return queryset

    def queryset_map_callable(self, obj):
        envios_carried = Envio.objects.filter(
            carrier=obj,
            status=Envio.STATUS_MOVING
        ).count()
        return (obj, envios_carried)

    def get_verbose_name_plural(self):
        return "Usuarios"


def get_employees_queryset(
        query: str = None, order_by_key: str = 'last_name',
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
        ).order_by('is_active', order_by_key).distinct())))


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
def create_user_view(request):
    context = {
        'selected_tab': 'accounts-tab',
        'client_list': Client.objects.all(),
    }
    form = CreateAccountForm()
    if request.method == 'POST':
        form = CreateAccountForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            account = form.save(commit=False)
            account.set_password(settings.DEFAULT_RESET_PASSWORD)
            account.save()
            if account.role == "admin":
                group = Group.objects.get(name='Admins')
            if account.role == "client":
                group = Group.objects.get(name='Clients')
            if account.role == "level_1":
                group = Group.objects.get(name='Level 1')
            if account.role == "level_2":
                group = Group.objects.get(name='Level 2')
            account.groups.add(group)
            account.save()
            msg = 'El usuario "{}" se creó correctamente.'.format(
                account.full_name.title()
            )
            return create_alert_and_redirect(
                request, msg, 'account:employees-list')
    context['form'] = form
    return render(request, 'account/employees_files/add.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def update_user_view(request, pk):
    context = {
        'selected_tab': 'accounts-tab',
        'client_list': Client.objects.all(),
    }
    account = get_object_or_404(Account, pk=pk)
    form = UpdateAccountForm(instance=account)

    if account.profile_picture:
        context['profile_picture'] = {
            'url': account.profile_picture.url,
            'text': truncate_start(account.profile_picture.url),
        }
    if account.dni_img:
        context['dni_img'] = {
            'url': account.dni_img.url,
            'text': truncate_start(account.dni_img.url),
        }
    if account.driver_license:
        context['driver_license'] = {
            'url': account.driver_license.url,
            'text': truncate_start(account.driver_license.url),
        }
    if account.criminal_record:
        context['criminal_record'] = {
            'url': account.criminal_record.url,
            'text': truncate_start(account.criminal_record.url),
        }
    if account.vtv:
        context['vtv'] = {
            'url': account.vtv.url,
            'text': truncate_start(account.vtv.url),
        }
    if account.insurance:
        context['insurance'] = {
            'url': account.insurance.url,
            'text': truncate_start(account.insurance.url),
        }
    if account.cedula:
        context['cedula'] = {
            'url': account.cedula.url,
            'text': truncate_start(account.cedula.url),
        }

    if request.method == 'POST':
        form = UpdateAccountForm(request.POST or None,
                                 request.FILES or None,
                                 instance=account)
        if form.is_valid():
            account = form.save(commit=False)
            account.save()
            account.groups.clear()
            if account.role == "admin":
                group = Group.objects.get(name='Admins')
            if account.role == "client":
                group = Group.objects.get(name='Clients')
            if account.role == "level_1":
                group = Group.objects.get(name='Level 1')
            if account.role == "level_2":
                group = Group.objects.get(name='Level 2')
            account.groups.add(group)
            account.save()
            msg = 'El usuario "{}" se actualizó correctamente.'.format(
                account.full_name.title()
            )
            return update_alert_and_redirect(
                request, msg, 'account:employees-list')
    context['form'] = form
    return render(request, 'account/employees_files/edit.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def employee_detail_view(request, pk):
    context = {}
    account = get_object_or_404(Account, pk=pk)
    context['account'] = account
    context['selected_tab'] = 'accounts-tab'
    context['envios'] = Envio.objects.filter(
        carrier__id=account.pk, status__in=[Envio.STATUS_MOVING]
    ).order_by('-date_created')
    return render(request, 'account/employees_files/detail.html', context)


@login_required(login_url='/login/')
@allowed_users(roles="Admins")
def account_delete_view(request, pk, **kwargs):

    delete_utility = DeleteObjectsUtil(
        model=Account,
        model_ids=pk,
        order_by='date_created',
        request=request,
        selected_tab='accounts-tab'
    )

    context = {}
    if request.method == 'POST':
        form = CheckPasswordForm(request.POST or None,
                                 current_password=request.user.password)
        if form.is_valid():
            delete_utility.delete_objects()
            delete_utility.create_alert()
            return redirect('clients:list')
    else:  # Meaning is a GET request
        form = CheckPasswordForm()
    context = delete_utility.get_context_data()
    context['form'] = form
    client = get_object_or_404(Client, pk=pk)
    context['client'] = client
    context['deposits'] = client.deposit_set.all()
    context['discounts'] = client.discount_set.all()
    return render(request, "clients/delete.html", context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def ajax_password_reset(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.set_password(settings.DEFAULT_RESET_PASSWORD)
    token: Token = Token.objects.filter(user=account)
    new_key = token[0].generate_key()
    token.update(key=new_key)
    account.has_to_reset_password = True
    account.save()
    return JsonResponse({'status': 'ok'})


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def enable_account_and_return_to_detail_view(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.set_password(settings.DEFAULT_RESET_PASSWORD)
    account.is_active = True
    token: Token = Token.objects.filter(user=account)
    new_key = token[0].generate_key()
    token.update(key=new_key)
    account.has_to_reset_password = True
    account.save()
    return employee_detail_view(request, pk)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def disable_account_and_return_to_detail_view(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.set_password(settings.DEFAULT_RESET_PASSWORD)
    account.is_active = False
    token: Token = Token.objects.filter(user=account)
    new_key = token[0].generate_key()
    token.update(key=new_key)
    account.has_to_reset_password = True
    account.save()
    return employee_detail_view(request, pk)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "Clients", "Level 1", "Level 2"])
def reset_password_view(request):
    form = PasswordResetForm()
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save()
            alerts = request.session.get('alerts', [])
            # Get current time
            now = datetime.now()
            # Create the alert
            alert = ToastAlert('password-reset', 'success',
                               'La contraseña se actualizó con éxito.',
                               'La contraseña se actualizó con éxito.', now)
            # Append it to already existing ones
            alerts.append(alert.get_as_dict())
            # Set them back to request's session
            request.session['alerts'] = alerts
            return login_view(request)
    context = {'form': form}
    return render(request, 'account/reset_password.html', context)
