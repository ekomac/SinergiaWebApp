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
from places.models import Partido, Town, Zone
from tracking.tracking_funcs import deposit
from utils.alerts.views import create_alert_and_redirect


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def index_view(request) -> HttpResponse:
    # If user is not an admin or tier1, skip to deposit selection
    if not request.user.groups.filter(
            name__in=["Admins", "Level 1"]).exists():
        return redirect('app_deposit:select-deposit',
                        carrier_pk=request.user.pk)
    carriers = Account.objects.filter(
        envios_carried_by__isnull=False
    ).annotate(envios=Count('envios_carried_by')).order_by('envios').distinct()
    context = {
        'carriers': carriers,
        'can_watch_other': 1
    }
    if not request.user.groups.filter(
            name__in=["Admins", "Level 1"]).exists():
        context['carriers'] = carriers.filter(pk=request.user.pk)
        context['can_watch_other'] = 0
    return render(request, 'app_deposit/index.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def select_deposit_view(request, carrier_pk):
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    context['carrier'] = carrier
    context['deposits'] = Deposit.objects.filter(client__isnull=True)
    return render(request, 'app_deposit/select_deposit.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def carrier_view(request, carrier_pk, deposit_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    context['carrier'] = carrier
    context['deposit'] = get_object_or_404(Deposit, pk=deposit_pk)
    context['envios_count'] = Envio.objects.filter(
        carrier=carrier, status=Envio.STATUS_MOVING).count()
    return render(request, 'app_deposit/carrier.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def confirm_all_view(request, carrier_pk, deposit_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    _deposit = get_object_or_404(Deposit, pk=deposit_pk)
    context['carrier'] = carrier
    context['deposit'] = _deposit
    envios = Envio.objects.filter(carrier=carrier, status=Envio.STATUS_MOVING)
    context['envios'] = envios
    context['envios_count'] = envios.count()
    print("carrier", carrier.username)
    if request.method == 'POST':
        deposit(
            author=request.user,
            deposit=_deposit,
            carrier=carrier,
        )
        msg = 'Los envíos se retiraron correctamente'
        return create_alert_and_redirect(request, msg, 'index')
    return render(request, 'app_deposit/confirm_all.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def scan_view(request, carrier_pk, deposit_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    context['carrier'] = carrier
    context['deposit'] = get_object_or_404(Deposit, pk=deposit_pk)
    envios = Envio.objects.filter(
        status__in=[Envio.STATUS_MOVING], carrier=carrier
    )
    context['ids'] = "-".join(list(map(lambda x: str(x.pk), envios)))
    return render(request, 'app_deposit/scan.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def confirm_scanned_view(request, carrier_pk, deposit_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    _deposit = get_object_or_404(Deposit, pk=deposit_pk)
    context['carrier'] = carrier
    context['deposit'] = _deposit
    if request.method == 'GET':
        envio_id = request.GET.get('envio_id')
        context['envio'] = get_object_or_404(Envio, pk=envio_id)
        context['envio_id'] = envio_id
        context['envios_count'] = Envio.objects.filter(carrier=carrier).count()
    if request.method == 'POST':
        envio_id = int(request.POST.get('envio_id'))
        deposit(
            author=request.user,
            carrier=carrier,
            deposit=_deposit,
            envios_ids=[envio_id]
        )
        msg = 'El envío se depositó correctamente'
        return create_alert_and_redirect(request, msg, 'index')
    return render(request, 'app_deposit/confirm_scanned.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def filter_by_view(request, carrier_pk, deposit_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    context['carrier'] = carrier
    context['deposit'] = get_object_or_404(Deposit, pk=deposit_pk)
    context['envios_count'] = carrier.envios_carried_by.count()
    return render(request, 'app_deposit/select_filter_by.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def confirmed_filtered_view(request, carrier_pk, deposit_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    _deposit = get_object_or_404(Deposit, pk=deposit_pk)
    context['carrier'] = carrier
    context['deposit'] = _deposit
    context['envios_count'] = carrier.envios_carried_by.count()

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
        deposit(
            author=request.user,
            carrier=carrier,
            deposit=_deposit,
            **filters
        )
        msg = 'Los envíos se depositaron correctamente'
        return create_alert_and_redirect(request, msg, 'index')
    return render(request, 'app_deposit/confirmed_filtered.html', context)
