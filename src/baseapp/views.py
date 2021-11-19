from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404, render

from account.decorators import allowed_users
from account.models import Account
from clients.models import Client
from envios.models import Envio, TrackingMovement
from places.models import Zone, Partido, Town
from utils.alerts.views import create_alert_and_redirect

from .basic_movements import withdraw_movement


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
def app_view(request):

    return render(request, 'baseapp/index.html', {})


# ############################ ! ORIGIN ##############################
@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def origin_index_view(request):
    context = {'clients': Client.objects.annotate(
        num_envios=Count(
            'envio', filter=Q(
                envio__shipment_status=Envio.STATUS_NEW
            )
        )
    ).order_by('-num_envios')}
    return render(request, 'baseapp/origin/index.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def origin_client_view(request, pk):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    context['client'] = client
    context['envios_count'] = client.envio_set.filter(
        shipment_status=Envio.STATUS_NEW,
        client=client
    ).order_by('-id').count()
    return render(request, 'baseapp/origin/client.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def origin_select_all_confirm_view(request, pk):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    envios = Envio.objects.filter(
        shipment_status=Envio.STATUS_NEW, client=client)
    context['client'] = client
    context['envios'] = envios
    context['envios_count'] = client.envio_set.filter(
        shipment_status=Envio.STATUS_NEW,
        client=client
    ).order_by('-id').count()
    if request.method == 'POST':
        user = request.user
        withdraw_movement(

            carrier=user,
            client=client
        )
        msg = 'Los envíos se retiraron correctamente'
        return create_alert_and_redirect(request, msg, 'baseapp:index')
    return render(request, 'baseapp/origin/confirm_all.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def origin_select_id_view(request, pk):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    context['client'] = client
    envios = Envio.objects.filter(
        shipment_status=Envio.STATUS_NEW, client=client)
    context['ids'] = "-".join(list(map(lambda x: str(x.pk), envios)))
    return render(request, 'baseapp/origin/select_id.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def origin_select_one_confirm_view(request, pk):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    context['client'] = client
    if request.method == 'GET':
        envio_id = request.GET.get('envio_id')
        context['envio'] = get_object_or_404(Envio, pk=envio_id)
        context['envio_id'] = envio_id
    if request.method == 'POST':
        print(request.POST)
        envio_id = int(request.POST.get('envio_id'))
        user = request.user
        withdraw_movement(
            carrier=user,
            client=client,
            envios_ids=[envio_id]
        )
        msg = 'El envío se retiró correctamente'
        return create_alert_and_redirect(request, msg, 'baseapp:index')
    return render(request, 'baseapp/origin/confirm_one.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def origin_select_filter_type_view(request, pk):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    context['client'] = client
    context['envios_count'] = client.envio_set.filter(
        shipment_status=Envio.STATUS_NEW,
        client=client
    ).order_by('-id').count()
    return render(request, 'baseapp/origin/select_filtered.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def origin_select_by_filter_view(request, pk):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    context['client'] = client

    if request.method == 'GET':
        filter_by = request.GET.get('filter_by')
        context['filter_by'] = filter_by

        if filter_by == 'zone':
            context['filter_by_name'] = 'zonas'
            context['objects'] = Zone.objects.filter(
                partido__town__envio__shipment_status=Envio.STATUS_NEW,
                partido__town__envio__client=client
            ).distinct().order_by('name')
        elif filter_by == 'partido':
            context['filter_by_name'] = 'partidos'
            context['objects'] = Partido.objects.filter(
                town__envio__shipment_status=Envio.STATUS_NEW,
                town__envio__client=client
            ).distinct().order_by('name')
        elif filter_by == 'town':
            context['filter_by_name'] = 'localidades'
            context['objects'] = Town.objects.filter(
                envio__shipment_status=Envio.STATUS_NEW,
                envio__client=client
            ).distinct().order_by('name')

    if request.method == 'POST':
        print(request.POST)
        filter_by = request.POST.get('filter_by')
        selected_ids = request.POST.get('selected_ids').split("-")
        filters = {}
        if filter_by == 'zone':
            filters = {"recipient_town__partido__zone__id__in": selected_ids}
        elif filter_by == 'partido':
            filters = {"recipient_town__partido__id__in": selected_ids}
        else:
            filters = {"recipient_town__id__in": selected_ids}
        user = request.user
        withdraw_movement(
            author=user,
            carrier=user,
            client=client,
            **filters
        )
        msg = 'Los envíos se retiraron correctamente'
        return create_alert_and_redirect(request, msg, 'baseapp:index')
    context['envios_count'] = client.envio_set.filter(
        shipment_status=Envio.STATUS_NEW,
        client=client
    ).order_by('-id').count()
    return render(request, 'baseapp/origin/confirm_filter_by.html', context)
# ############################## ! ORIGIN ##############################


# ############################## ! CENTRAL ##############################
@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def central_index_view(request):
    context = {}
    context['users'] = Account.objects.filter(
        carrier__action=TrackingMovement.ACTION_RECOLECTION,
        carrier__result=TrackingMovement.RESULT_TRANSFERED,
        carrier__envios__shipment_status=Envio.STATUS_MOVING
    ).distinct().annotate(
        envios=Count(
            'carrier',
            filter=Q(carrier__action=TrackingMovement.ACTION_RECOLECTION) |
            Q(carrier__result=TrackingMovement.RESULT_TRANSFERED) |
            Q(carrier__envios__shipment_status=Envio.STATUS_MOVING)
        )
    ).order_by('-envios')
    return render(request, 'baseapp/central/index.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def central_receive_user_view(request, pk):
    context = {}
    context['users'] = Account.objects.filter(
        carrier__action=TrackingMovement.ACTION_RECOLECTION,
        carrier__result=TrackingMovement.RESULT_TRANSFERED,
        carrier__envios__shipment_status=Envio.STATUS_MOVING
    ).distinct().annotate(
        envios=Count(
            'carrier',
            filter=Q(carrier__action=TrackingMovement.ACTION_RECOLECTION) |
            Q(carrier__result=TrackingMovement.RESULT_TRANSFERED) |
            Q(carrier__envios__shipment_status=Envio.STATUS_MOVING)
        )
    ).order_by('-envios')
    return render(request, 'baseapp/central/index.html', context)
# ############################ ! CENTRAL ##############################
