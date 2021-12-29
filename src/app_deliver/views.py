# Djano
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Count
from django.http.response import HttpResponse
from django.shortcuts import redirect, render

# Project
from account.decorators import allowed_users
from account.models import Account
from app_deliver.decorators import deliver_safe
from envios.models import Envio


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
@deliver_safe(redirect_app='index')
def index_view(request) -> HttpResponse:

    # If user is not an admin or a tier1, skip to scan
    if not request.user.groups.filter(
            name__in=settings.DELIVER_IN_NAME_OF_OTHERS).exists():
        return redirect('app_deliver:scan',
                        carrier_pk=request.user.pk)
    carriers = Account.objects.filter(
        Carrier__isnull=False
    ).annotate(envios=Count('Carrier')).order_by('envios').distinct()
    context = {
        'carriers': carriers
    }
    return render(request, 'app_deliver/index.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
@deliver_safe(redirect_app='index')
def scan_view(request) -> HttpResponse:
    context = {}
    envios = Envio.objects.filter(
        status__in=[Envio.STATUS_MOVING], carrier=request.user)
    context['c_envios_count'] = envios.count()
    context['ids'] = "-".join(list(map(lambda x: str(x.pk), envios)))
    return render(request, 'app_deliver/scan.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
@deliver_safe(redirect_app='index')
def select_result_view(request):
    envio_id = request.GET.get('eid')
    print(f"{envio_id=}")
    context = {
        'envio': Envio.objects.get(pk=envio_id),
        'envio_id': envio_id,
        'c_envios_count': Envio.objects.filter(
            carrier=request.user,
            status__in=[Envio.STATUS_MOVING]).count()
    }
    return render(request, 'app_deliver/select_result.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
@deliver_safe(redirect_app='index')
def confirm_result_view(request):
    context = {}
    return render(request, 'app_deliver/confirm_scanned.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
@deliver_safe(redirect_app='index')
def confirm_other_view(request):
    context = {}
    return render(request, 'app_deliver/confirm_scanned.html', context)
