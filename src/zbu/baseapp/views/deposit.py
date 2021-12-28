# Django
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render

# Project
from account.decorators import allowed_users
from account.models import Account
from baseapp.api.api import deposit_movement
from envios.models import Envio
from places.models import Deposit
from utils.alerts.views import create_alert_and_redirect


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
def index_view(request) -> HttpResponse:
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
    return render(request, 'baseapp/deposit/index.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
def select_deposit_view(request, carrier_pk):
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    context['carrier'] = carrier
    context['deposits'] = Deposit.objects.all()
    return render(request, 'baseapp/deposit/select_deposit.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
def carrier_view(request, carrier_pk, deposit_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    context['carrier'] = carrier
    context['deposit'] = get_object_or_404(Deposit, pk=deposit_pk)
    context['envios_count'] = Envio.objects.filter(
        carrier=carrier, status=Envio.STATUS_MOVING).count()
    return render(request, 'baseapp/deposit/carrier.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
def select_all_confirm_view(request, carrier_pk, deposit_pk) -> HttpResponse:
    context = {}
    carrier = get_object_or_404(Account, pk=carrier_pk)
    deposit = get_object_or_404(Deposit, pk=deposit_pk)
    context['carrier'] = carrier
    context['deposit'] = deposit
    envios = Envio.objects.filter(carrier=carrier, status=Envio.STATUS_MOVING)
    context['envios'] = envios
    context['envios_count'] = envios.count()
    print("carrier", carrier.username)
    if request.method == 'POST':
        # user = request.user
        # insert_movement()
        deposit_movement(
            author=request.user,
            deposit=deposit,
            carrier=carrier,
        )
        msg = 'Los envíos se retiraron correctamente'
        return create_alert_and_redirect(request, msg, 'baseapp:index')
    return render(request, 'baseapp/deposit/confirm_all.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
def select_id_view(request, carrier_pk, deposit_pk) -> HttpResponse:
    raise NotImplementedError("TODO: Implement this view")
    context = {}
    return render(request, '', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def select_one_confirm_view(request, carrier_pk, deposit_pk) -> HttpResponse:
    raise NotImplementedError("TODO: Implement this view")
    context = {}
    return render(request, '', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def select_filter_type_view(request, carrier_pk, deposit_pk) -> HttpResponse:
    raise NotImplementedError("TODO: Implement this view")
    context = {}
    return render(request, '', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def select_by_filter_view(request, carrier_pk, deposit_pk) -> HttpResponse:
    raise NotImplementedError("TODO: Implement this view")
    context = {}
    return render(request, '', context)
