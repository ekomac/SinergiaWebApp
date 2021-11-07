from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404, redirect, render

from account.decorators import allowed_users
from clients.models import Client
from envios.models import Envio

from .basic_movements import withdraw_movement


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
def app_view(request):

    return render(request, 'baseapp/index.html', {})


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
    if request.method == 'POST':
        user = request.user
        withdraw_movement(
            carrier=user,
            client=client
        )
        return redirect('baseapp:index')
    return render(request, 'baseapp/origin/confirm_all.html', context)


@ login_required(login_url='/login/')
@ allowed_users(roles=["Admins", "EmployeeTier1"])
def origin_select_ids_view(request, pk):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    context['client'] = client
    return render(request, 'baseapp/origin/select_ids.html', context)


@ login_required(login_url='/login/')
@ allowed_users(roles=["Admins", "EmployeeTier1"])
def origin_select_filtered_view(request, pk):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    context['client'] = client
    return render(request, 'baseapp/origin/select_filtered.html', context)
