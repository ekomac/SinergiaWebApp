# Python
from typing import Any, Dict

# Django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render

# Project
from account.decorators import allowed_users, allowed_users_in_class_view
from clients.models import Client
from deposit.forms import CreateDepositForm
from deposit.models import Deposit
from envios.models import Envio
from places.utils import get_localidades_as_JSON
from places.models import Partido
from utils.forms import CheckPasswordForm
from utils.views import DeleteObjectsUtil, CompleteListView
from utils.alerts.views import (
    create_alert_and_redirect,
    update_alert_and_redirect
)


class DepositListView(CompleteListView, LoginRequiredMixin):

    template_name = 'deposit/list.html'
    model = Deposit
    decoders = (
        {
            'key': 'client_id',
            'filter': lambda x: 'client__isnull' if (
                x in [-1, '-1']) else 'client__id',
            'function': lambda x: True if x in [-1, '-1'] else int(x),
            'context': str,
        },
        {
            'key': 'is_active',
            'filter': 'is_active',
            'function': lambda x: True if x == 'true' else False,
            'context': lambda x: x,
        },
        {
            'key': 'has_envios',
            'filter': 'envio__isnull',
            'function': lambda x: True if x == 'true' else False,
            'context': lambda x: x,
        },
    )
    query_keywords = ('name__icontains', 'client__name__icontains',
                      'address__icontains', 'town__name__icontains')
    selected_tab = 'deposits-tab'

    @allowed_users_in_class_view(roles=["Admins"])
    def get(self, request):
        return super(DepositListView, self).get(request)

    def queryset_map_callable(self, obj):
        envios_in_deposit = Envio.objects.filter(
            deposit=obj,
            status__in=[Envio.STATUS_STILL, Envio.STATUS_NEW, ]).count()
        return (obj, envios_in_deposit)

    def get_context_data(self) -> Dict[str, Any]:
        context = super().get_context_data()
        context['clients'] = Client.objects.all()
        return context


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def deposit_create_view(request):

    form = CreateDepositForm()
    if request.method == 'POST':
        form = CreateDepositForm(
            request.POST, request.FILES)
        if form.is_valid():
            deposit = form.save()
            deposit.created_by = request.user
            deposit.is_sinergia = deposit.client is None
            deposit.save()
            msg = f'El depósito "{deposit}" se creó correctamente.'
            return create_alert_and_redirect(
                request, msg, 'deposits:detail', deposit.pk)
    context = {
        'form': form,
        'selected_tab': 'deposits-tab',
        'partidos': Partido.objects.all().order_by("name"),
        'places': get_localidades_as_JSON(),
    }
    return render(request, 'deposit/add.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def deposit_edit_view(request, pk):

    if request.method == 'POST':
        form = CreateDepositForm(request.POST, request.FILES,
                                 instance=Deposit.objects.get(pk=pk))
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.is_sinergia = deposit.client is None
            deposit.save()
            msg = f'El depósito "{deposit}" se actualizó correctamente.'
            return update_alert_and_redirect(
                request, msg, 'deposits:detail', pk)
    else:
        form = CreateDepositForm(
            instance=Deposit.objects.get(pk=pk))
    context = {
        'form': form,
        'selected_tab': 'deposits-tab',
        'partidos': Partido.objects.all().order_by("name"),
        'deposit': Deposit.objects.get(pk=pk),
        'places': get_localidades_as_JSON(),
    }
    return render(request, 'deposit/edit.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def activate_deposit_view(request, pk):
    deposit = get_object_or_404(Deposit, pk=pk)
    deposit.is_active = True
    deposit.save()
    msg = f'El depósito "{deposit}" se habilitó correctamente.'
    return create_alert_and_redirect(
        request, msg, 'deposits:detail', pk)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def deactivate_deposit_view(request, pk):
    deposit = get_object_or_404(Deposit, pk=pk)
    deposit.is_active = False
    deposit.save()
    msg = f'El depósito "{deposit}" se inhabilitó correctamente.'
    return create_alert_and_redirect(
        request, msg, 'deposits:detail', pk)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def deposit_detail_view(request, pk):
    ctx = {}
    deposit = get_object_or_404(Deposit, pk=pk)
    ctx['deposit'] = deposit
    ctx['selected_tab'] = 'deposits-tab'
    ctx['envios'] = Envio.objects.filter(
        deposit__id=deposit.pk, status__in=[
            Envio.STATUS_STILL, Envio.STATUS_NEW]).order_by('-date_created')
    return render(request, 'deposit/detail.html', ctx)


@login_required(login_url='/login/')
@allowed_users(roles="Admins")
def deposit_delete_view(request, pk):

    delete_utility = DeleteObjectsUtil(
        model=Deposit,
        model_ids=pk,
        order_by='name',
        request=request,
        selected_tab='deposits-tab'
    )

    context = {}
    if request.method == 'POST':
        form = CheckPasswordForm(request.POST or None,
                                 current_password=request.user.password)
        if form.is_valid():
            delete_utility.delete_objects()
            delete_utility.create_alert()
            return redirect('deposits:list')
    else:  # Meaning is a GET request
        form = CheckPasswordForm()
    context = delete_utility.get_context_data()
    context['form'] = form
    deposit = get_object_or_404(Deposit, pk=pk)
    context['deposit'] = deposit
    return render(request, "deposit/delete.html", context)
