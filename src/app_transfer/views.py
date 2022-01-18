# Python module
import json

# Django
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

# Project
from account.decorators import allowed_users
from account.models import Account
from app_transfer.decorators import transfer_safe
from envios.models import Envio
from places.models import Partido, Town, Zone
from tracking.tracking_funcs import transfer
from utils.alerts.views import create_alert_and_redirect


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
@transfer_safe(roles=["Admins", "EmployeeTier1"], redirect_app='index')
def index_view(request) -> HttpResponse:
    # If user is not an admin or a tier1, skip to receiver selection
    if not request.user.groups.filter(
            name__in=["Admins", "EmployeeTier1"]).exists():
        return redirect('app_transfer:select-receiver',
                        carrier_pk=request.user.pk)
    carriers = Account.objects.filter(
        Carrier__isnull=False
    ).annotate(envios=Count('Carrier')).order_by('envios').distinct()
    context = {
        'carriers': carriers,
        'can_watch_other': 1
    }
    if not request.user.groups.filter(
            name__in=["Admins", "EmployeeTier1"]).exists():
        context['carriers'] = carriers.filter(pk=request.user.pk)
        context['can_watch_other'] = 0
    return render(request, 'app_transfer/index.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
@transfer_safe(roles=["Admins", "EmployeeTier1"], redirect_app='index')
def select_receiver_view(request, carrier_pk):
    context = {}
    # Get the current carrier
    carrier = get_object_or_404(Account, pk=carrier_pk)
    context['carrier'] = carrier
    # Get the carrier as JSON
    context['carrier_JSON'] = json.dumps(
        carrier, default=str, sort_keys=True, indent=4
    )
    # Get receivers which are employees
    receivers = Account.objects.filter(
        groups__name__in=['Admins', 'EmployeeTier1', 'EmployeeTier2']
    ).exclude(pk=carrier_pk).annotate(
        envios=Count('Carrier')).order_by('envios').distinct().values(
        "pk", "username", "first_name", "last_name", "envios")
    # Parse them to list of JSON
    receivers = [json.dumps(receiver, indent=4) for receiver in receivers]
    # Parse the list to JSON for template
    context['receivers'] = json.dumps(receivers)
    return render(request, 'app_transfer/select_receiver.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
@transfer_safe(roles=["Admins", "EmployeeTier1"], redirect_app='index')
def carrier_view(request, carrier_pk, receiver_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    receiver = get_object_or_404(Account, pk=receiver_pk)
    context['carrier'] = carrier
    context['receiver'] = receiver
    context['c_envios_count'] = Envio.objects.filter(
        carrier=carrier, status=Envio.STATUS_MOVING).count()
    context['r_envios_count'] = Envio.objects.filter(
        carrier=receiver, status=Envio.STATUS_MOVING).count()
    return render(request, 'app_transfer/carrier.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
@transfer_safe(roles=["Admins", "EmployeeTier1"], redirect_app='index')
def confirm_all_view(request, carrier_pk, receiver_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    receiver = get_object_or_404(Account, pk=receiver_pk)
    context['carrier'] = carrier
    context['receiver'] = receiver
    envios = Envio.objects.filter(carrier=carrier, status=Envio.STATUS_MOVING)
    context['envios'] = envios
    context['c_envios_count'] = envios.count()
    context['r_envios_count'] = Envio.objects.filter(
        carrier=receiver, status=Envio.STATUS_MOVING).count()
    if request.method == 'POST':
        transfer(
            author=request.user,
            receiver=receiver,
            carrier=carrier,
        )
        msg = 'Los envíos se transfirieron correctamente'
        return create_alert_and_redirect(request, msg, 'index')
    return render(request, 'app_transfer/confirm_all.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
@transfer_safe(roles=["Admins", "EmployeeTier1"], redirect_app='index')
def scan_view(request, carrier_pk, receiver_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    context['carrier'] = carrier
    receiver = get_object_or_404(Account, pk=receiver_pk)
    context['receiver'] = receiver
    envios = Envio.objects.filter(status=Envio.STATUS_MOVING, carrier=carrier)
    context['ids'] = "-".join(list(map(lambda x: str(x.pk), envios)))
    context['c_envios_count'] = envios.count()
    context['r_envios_count'] = Envio.objects.filter(
        carrier=receiver, status=Envio.STATUS_MOVING).count()
    return render(request, 'app_transfer/scan.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
@transfer_safe(roles=["Admins", "EmployeeTier1"], redirect_app='index')
def confirm_scanned_view(request, carrier_pk, receiver_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    receiver = get_object_or_404(Account, pk=receiver_pk)
    context['carrier'] = carrier
    context['receiver'] = receiver
    if request.method == 'GET':
        envio_id = request.GET.get('envio_id')
        context['envio'] = get_object_or_404(Envio, pk=envio_id)
        context['envio_id'] = envio_id
        context['c_envios_count'] = Envio.objects.filter(
            carrier=carrier, status=Envio.STATUS_MOVING).count()
        context['r_envios_count'] = Envio.objects.filter(
            carrier=receiver, status=Envio.STATUS_MOVING).count()
    if request.method == 'POST':
        envio_id = int(request.POST.get('envio_id'))
        transfer(
            author=request.user,
            carrier=carrier,
            receiver=receiver,
            envios_ids=[envio_id]
        )
        msg = 'El envío se transfirieron correctamente'
        return create_alert_and_redirect(request, msg, 'index')
    return render(request, 'app_transfer/confirm_scanned.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
@transfer_safe(roles=["Admins", "EmployeeTier1"], redirect_app='index')
def filter_by_view(request, carrier_pk, receiver_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    context['carrier'] = carrier
    receiver = get_object_or_404(Account, pk=receiver_pk)
    context['receiver'] = receiver
    context['c_envios_count'] = Envio.objects.filter(
        carrier=carrier, status=Envio.STATUS_MOVING).count()
    context['r_envios_count'] = Envio.objects.filter(
        carrier=receiver, status=Envio.STATUS_MOVING).count()
    return render(request, 'app_transfer/select_filter_by.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
@transfer_safe(roles=["Admins", "EmployeeTier1"], redirect_app='index')
def confirm_filtered_view(request, carrier_pk, receiver_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    receiver = get_object_or_404(Account, pk=receiver_pk)
    context['carrier'] = carrier
    context['receiver'] = receiver
    context['c_envios_count'] = Envio.objects.filter(
        carrier=carrier, status=Envio.STATUS_MOVING).count()
    context['r_envios_count'] = Envio.objects.filter(
        carrier=receiver, status=Envio.STATUS_MOVING).count()

    if request.method == 'GET':
        filter_by = request.GET.get('filter_by')
        context['filter_by'] = filter_by

        if filter_by == 'zone':
            context['filter_by_name'] = 'zonas'
            filter_1 = 'partido__town__destination__receiver__envio__status'
            filter_2 = 'partido__town__destination' +\
                '__receiver__envio__carrier_id'
            filters = {
                filter_1: Envio.STATUS_MOVING,
                filter_2: carrier.pk
            }
            context['objects'] = Zone.objects.filter(
                **filters).distinct().order_by('name')

        elif filter_by == 'partido':
            context['filter_by_name'] = 'partidos'
            context['objects'] = Partido.objects.filter(
                town__destination__receiver__envio__status=Envio.STATUS_MOVING,
                town__destination__receiver__envio__carrier_id=carrier.pk
            ).distinct().order_by('name')

        elif filter_by == 'town':
            context['filter_by_name'] = 'localidades'
            context['objects'] = Town.objects.filter(
                destination__receiver__envio__status=Envio.STATUS_MOVING,
                destination__receiver__envio__carrier_id=carrier.pk
            ).distinct().order_by('name')

    if request.method == 'POST':
        filter_by = request.POST.get('filter_by')
        selected_ids = request.POST.get('selected_ids').split("-")
        filters = {}
        if filter_by == 'zone':
            filters = {'town__partido__zone__pk__in': selected_ids}
        elif filter_by == 'partido':
            filters = {'town__partido__pk__in': selected_ids}
        else:
            filters = {'town__pk__in': selected_ids}
        transfer(
            author=request.user,
            carrier=carrier,
            receiver=receiver,
            **filters
        )
        msg = 'Los envíos se trasnfirieron correctamente'
        return create_alert_and_redirect(request, msg, 'index')
    return render(request, 'app_transfer/confirmed_filtered.html', context)
