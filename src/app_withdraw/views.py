# Main library
import json

# Django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

# Project
from account.decorators import allowed_users
from account.models import Account
from deposit.models import Deposit
from envios.models import Envio
from places.models import Zone, Partido, Town
from tracking.tracking_funcs import withdraw
from utils.alerts.views import create_alert_and_redirect


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def index_view(request) -> HttpResponse:
    deposits = Deposit.objects.annotate(
        num_envios=Count(
            'envio'
        )).order_by('-num_envios')
    deposits = [deposit for deposit in deposits if deposit.num_envios > 0]
    context = {
        'deposits': deposits,
    }
    return render(request, 'app_withdraw/index.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def select_carrier_view(request, deposit_pk) -> HttpResponse:
    context = {}
    # Get the current deposit
    deposit = get_object_or_404(Deposit, pk=deposit_pk)
    context['deposit'] = deposit

    # If user is not an admin or a tier1, skip the next step
    if not request.user.groups.filter(
            name__in=["Admins", "Level 1"]).exists():
        return redirect(
            'app_withdraw:deposit', deposit_pk=deposit_pk,
            carrier_pk=request.user.pk
        )

    # If step not skipped, get the deposit as JSON
    context['deposit_JSON'] = json.dumps(
        deposit, default=str, sort_keys=True, indent=4
    )
    # Get carriers which are employees
    carriers = Account.objects.filter(
        groups__name__in=['Admins', 'Level 1', 'Level 2']
    ).annotate(envios=Count('envios_carried_by')).order_by(
        'envios').distinct().values(
            "pk", "username", "first_name", "last_name", "envios")
    # Parse them to list of JSON
    carriers = [json.dumps(carrier, indent=4) for carrier in carriers]
    # Parse the list to JSON for template
    context['carriers'] = json.dumps(carriers)
    return render(request, 'app_withdraw/select_carrier.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def deposit_view(request, deposit_pk, carrier_pk) -> HttpResponse:
    context = {}
    deposit = get_object_or_404(Deposit, pk=deposit_pk)
    context['deposit'] = deposit
    context['carrier'] = get_object_or_404(Account, pk=carrier_pk)
    context['envios_count'] = deposit.envio_set.count()
    return render(request, 'app_withdraw/deposit.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def confirm_all_view(request, deposit_pk, carrier_pk) -> HttpResponse:
    context = {}
    deposit = get_object_or_404(Deposit, pk=deposit_pk)
    context['deposit'] = deposit
    envios = Envio.objects.filter(
        status__in=[Envio.STATUS_NEW, Envio.STATUS_STILL],
        deposit=deposit)
    context['envios'] = envios
    context['envios_count'] = envios.count()
    context['carrier'] = get_object_or_404(Account, pk=carrier_pk)
    if request.method == 'POST':
        user = request.user
        withdraw(
            author=user,
            carrier=user,
            deposit=deposit
        )
        msg = 'Los envíos se retiraron correctamente'
        return create_alert_and_redirect(request, msg, 'index')
    return render(request, 'app_withdraw/confirm_all.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def scan_view(request, deposit_pk, carrier_pk) -> HttpResponse:
    context = {}
    deposit = get_object_or_404(Deposit, pk=deposit_pk)
    context['deposit'] = deposit
    context['carrier'] = get_object_or_404(Account, pk=carrier_pk)
    envios = Envio.objects.filter(
        status__in=[Envio.STATUS_NEW, Envio.STATUS_STILL], deposit=deposit)
    context['ids'] = "-".join(list(map(lambda x: str(x.pk), envios)))
    return render(request, 'app_withdraw/scan.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def confirm_scanned_view(request, deposit_pk, carrier_pk) -> HttpResponse:
    context = {}
    deposit = get_object_or_404(Deposit, pk=deposit_pk)
    context['deposit'] = deposit
    carrier = get_object_or_404(Account, pk=carrier_pk)
    context['carrier'] = carrier
    envios_count = deposit.envio_set.count()
    context['envios_count'] = envios_count
    if request.method == 'GET':
        envio_id = request.GET.get('envio_id')
        context['envio'] = get_object_or_404(Envio, pk=envio_id)
        context['envio_id'] = envio_id
    if request.method == 'POST':
        print(request.POST)
        envio_id = int(request.POST.get('envio_id'))
        withdraw(
            author=request.user,
            carrier=carrier,
            deposit=deposit,
            envios_ids=[envio_id]
        )
        msg = 'El envío se retiró correctamente'
        return create_alert_and_redirect(request, msg, 'index')
    return render(request, 'app_withdraw/confirm_scanned.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def filter_by_view(request, deposit_pk, carrier_pk) -> HttpResponse:
    context = {}
    deposit = get_object_or_404(Deposit, pk=deposit_pk)
    context['deposit'] = deposit
    context['carrier'] = get_object_or_404(Account, pk=carrier_pk)
    context['envios_count'] = deposit.envio_set.count()
    return render(request, 'app_withdraw/select_filter_by.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def confirm_filtered_view(request, deposit_pk, carrier_pk) -> HttpResponse:
    context = {}
    deposit = get_object_or_404(Deposit, pk=deposit_pk)
    carrier = get_object_or_404(Account, pk=carrier_pk)
    context['carrier'] = carrier
    context['deposit'] = deposit
    context['envios_count'] = deposit.envio_set.count()

    if request.method == 'GET':
        filter_by = request.GET.get('filter_by')
        context['filter_by'] = filter_by

        if filter_by == 'zone':
            context['filter_by_name'] = 'zonas'
            filters = {
                'partido__town__destination__receiver__envio__status__in': [
                    Envio.STATUS_NEW,
                    Envio.STATUS_STILL
                ],
                'partido__town__destination__receiver__envio__deposit': deposit
            }
            context['objects'] = Zone.objects.filter(
                **filters).distinct().order_by('name')
        elif filter_by == 'partido':
            context['filter_by_name'] = 'partidos'
            filters = {
                'town__destination__receiver__envio__status__in': [
                    Envio.STATUS_NEW,
                    Envio.STATUS_STILL,
                ],
                'town__destination__receiver__envio__deposit': deposit
            }
            context['objects'] = Partido.objects.filter(
                **filters).distinct().order_by('name')
        elif filter_by == 'town':
            context['filter_by_name'] = 'localidades'
            context['objects'] = Town.objects.filter(
                destination__receiver__envio__status__in=[
                    Envio.STATUS_NEW, Envio.STATUS_STILL],
                destination__receiver__envio__deposit=deposit
            ).distinct().order_by('name')

    if request.method == 'POST':
        filter_by = request.POST.get('filter_by')
        selected_ids = request.POST.get('selected_ids').split("-")
        filters = {}
        if filter_by == 'zone':
            filters = {"town__partido__zone__id__in": selected_ids}
        elif filter_by == 'partido':
            filters = {"town__partido__id__in": selected_ids}
        else:
            filters = {"town__id__in": selected_ids}
        user = request.user
        withdraw(
            author=user,
            carrier=carrier,
            deposit=deposit,
            **filters
        )
        msg = 'Los envíos se retiraron correctamente'
        return create_alert_and_redirect(request, msg, 'index')
    return render(request, 'app_withdraw/confirm_filtered.html', context)


def carriers_as_html_li(deposit_pk, carriers):
    return json.dumps(list(map(lambda carrier: carrier_as_html_li(
        deposit_pk, carrier), carriers)))


def carrier_as_html_li(deposit_pk, carrier):
    return f"""
    <li class="list-group-item list-group-item-action list-menu-item p-2"
        onclick="location.href='/app/withdraw/{deposit_pk}/to/{carrier.pk}'"
            style="cursor: pointer;">
        <div class="d-flex flex-row justify-content-between
            align-items-center my-2">
            <div class="d-flex flex-column flex-wrap
                justify-content-center align-items-bottom">
                <h6 class="p-0 m-0" style="color: rgb(90,90,90);">
                    <span class="badge bg-secondary">@{carrier.username}</span>
                </h6>
                <h4 class="p-0 m-0"
                    style="color: rgb(90,90,90);">
                    {carrier.first_name} {carrier.last_name}</h4>
                <div style="color: rgb(90,90,90);">
                    Portando&nbsp;{carrier.envios}&nbsp;envíos
                </div>
            </div>
            <i class="bi bi-chevron-right"></i>
        </div>
    </li>
    """
