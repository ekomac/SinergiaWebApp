from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count

from account.decorators import allowed_users
from clients.models import Client
from envios.models import Deposit, Envio


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
def app_view(request):

    return render(request, 'baseapp/index.html', {})


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def origin_index_view(request):
    context = {'clients': Client.objects.annotate(
        num_envios=Count('envio')).order_by('-num_envios')}
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
        # ! TODO Fx de withdraw
        return redirect('baseapp:index')
    return render(request, 'baseapp/origin/confirm_all.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def origin_select_specific_view(request, pk):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    context['client'] = client
    return render(request, 'baseapp/origin/select_specific.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def origin_select_some_view(request, pk):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    context['client'] = client
    return render(request, 'baseapp/origin/select_some.html', context)
