# Djano
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Count
from django.http.response import HttpResponse
from django.shortcuts import redirect, render

# Project
from account.decorators import allowed_users
from account.models import Account
from mobile.deliver.decorators import deliver_safe
from mobile.deliver .forms import DeliverForm
from envios.models import Envio
from tracking.tracking_funcs import delivery
from utils.alerts.views import create_alert_and_redirect


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
        envios_carried_by__isnull=False
    ).annotate(envios=Count('envios_carried_by')).order_by('envios').distinct()
    context = {
        'carriers': carriers
    }
    return render(request, 'mobile/deliver/index.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
@deliver_safe(redirect_app='index')
def scan_view(request) -> HttpResponse:
    context = {}
    envios = Envio.objects.filter(
        status__in=[Envio.STATUS_MOVING], carrier=request.user)
    context['c_envios_count'] = envios.count()
    context['ids'] = "-".join(list(map(lambda x: str(x.pk), envios)))
    return render(request, 'mobile/deliver/scan.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
@deliver_safe(redirect_app='index')
def select_result_view(request):
    envio_id = request.GET.get('eid') or request.POST.get('eid')
    envio = Envio.objects.get(pk=envio_id)
    form = DeliverForm()
    if request.method == 'POST':
        form = DeliverForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            envio = delivery(
                author=request.user,
                result_obtained=request.POST['result'],
                envio_id=request.POST['eid'],
                proof_file=request.FILES.get('proof', None),
                comment=request.POST.get('comment', None)
            )
            address = envio.full_address
            client = envio.client
            status = envio.get_status_display()
            msg = f"El envío a {address} de {client} se marcó como {status}"
            return create_alert_and_redirect(request, msg, 'index')
    context = {
        'form': form,
        'envio': envio,
        'envio_id': envio_id,
        'c_envios_count': Envio.objects.filter(
            carrier=request.user,
            status__in=[Envio.STATUS_MOVING]).count()
    }
    return render(request, 'mobile/deliver/select_result.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
@deliver_safe(redirect_app='index')
def confirm_result_view(request):
    context = {}
    return render(request, 'mobile/deliver/confirm_scanned.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
@deliver_safe(redirect_app='index')
def confirm_other_view(request):
    context = {}
    return render(request, 'mobile/deliver/confirm_scanned.html', context)
