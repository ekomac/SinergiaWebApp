# Basic Python
from typing import Any, Dict

# Django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render


# Project
from account.decorators import allowed_users, allowed_users_in_class_view
from account.models import Account
from clients.forms import CreateClientForm, CreateDiscountForm, EditClientForm
from clients.models import Client, Discount
from deposit.models import Deposit
from places.models import Partido
from places.utils import get_localidades_as_JSON
from utils.alerts.views import (
    create_alert_and_redirect, update_alert_and_redirect)
from utils.forms import CheckPasswordForm
from utils.views import CompleteListView, DeleteObjectsUtil, truncate_start


class ClientListView(CompleteListView, LoginRequiredMixin):
    template_name = 'clients/list.html'
    model = Client
    decoders = (
        {
            'key': 'has_discounts',
            'filter': 'discount__isnull',
            'function': lambda x: True if x == 'true' else False,
            'context': lambda x: x,
        },
        {
            'key': 'is_active',
            'filter': 'is_active',
            'function': lambda x: True if x == 'true' else False,
            'context': lambda x: x,
        },
    )
    query_keywords = (
        'name__icontains',
        'contact_name__icontains',
        'contact_phone__icontains',
        'contact_email__icontains',
    )

    @allowed_users_in_class_view(roles=["Admins"])
    def get(self, request):
        return super(ClientListView, self).get(request)

    def queryset_map_callable(self, obj):
        deposits = ", ".join(
            [depo.name for depo in Deposit.objects.filter(client=obj)])
        places_with_discounts = Partido.objects.filter(
            discount__client=obj).count()
        return (obj, deposits, places_with_discounts)

    def get_context_data(self) -> Dict[str, Any]:
        context = super().get_context_data()
        context['clients'] = Client.objects.all()
        context['selected_tab'] = 'clients-tab'
        return context


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def create_client_view(request):

    form = CreateClientForm()
    if request.method == 'POST':
        form = CreateClientForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            client = form.save()
            msg = f'El cliente "{client}" se creó correctamente.'
            return create_alert_and_redirect(
                request, msg, 'clients:detail', client.pk)
    context = {
        'form': form,
        'selected_tab': 'clients-tab',
        'partidos': Partido.objects.all().order_by("name"),
        'places': get_localidades_as_JSON(),
    }
    return render(request, 'clients/add.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def edit_client_view(request, pk):
    client = Client.objects.get(pk=pk)
    if request.method == 'POST':
        form = EditClientForm(request.POST, request.FILES,
                              instance=client)
        if form.is_valid():
            client = form.save(commit=False)
            client.save()
            msg = f'El cliente "{client}" se actualizó correctamente.'
            return update_alert_and_redirect(
                request, msg, 'clients:detail', pk)
    else:
        form = EditClientForm(instance=Client.objects.get(pk=pk))
    context = {
        'form': form,
        'selected_tab': 'clients-tab',
        'client': Client.objects.get(pk=pk),
    }
    if client.contract:
        context['contract'] = {
            'url': client.contract.url,
            'text': truncate_start(client.contract.url),
        }
    return render(request, 'clients/edit.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def client_detail_view(request, pk):
    client = get_object_or_404(Client, pk=pk)
    deposits = Deposit.objects.filter(client__id=client.id)
    deposits_count = deposits.count()
    discounts = Discount.objects.filter(client__id=client.id)
    discounts_count = discounts.count()
    discounts = list(map(map_discount_to_dict, discounts))
    users = Account.objects.filter(
        client__pk=client.pk,
        is_superuser=False,
    ).order_by('last_name', 'first_name', 'username')
    users_count = users.count()
    ctx = {}
    ctx['client'] = client
    ctx['selected_tab'] = 'clients-tab'
    ctx['discounts_count'] = discounts_count
    ctx['discounts'] = discounts
    ctx['deposits_count'] = deposits_count
    ctx['deposits'] = deposits
    ctx['contract'] = None
    ctx['users'] = users
    ctx['users_count'] = users_count
    if client.contract:
        ctx['contract'] = {
            'url': client.contract.url,
            'text': truncate_start(client.contract.url),
        }
    return render(request, 'clients/detail.html', ctx)


def map_discount_to_dict(discount: Discount) -> Dict[str, str]:
    """
    Maps a discount to a dict containing the discount's amount,
    the discount's type as a boolean and as a str, the partido's
    list as a str.

    Args:
        discount (Discount): the discount to be mapped.

    Returns:
        Dict[str, str]: the mapped discount.
    """
    return {
        'id': discount.id,
        'type': "Flex" if discount.is_for_flex else "Mensajería",
        'is_for_flex': discount.is_for_flex,
        'amount': discount.amount,
        'partidos': ", ".join(
            [partido.name.title(
            ) for partido in discount.partidos.all().order_by("name")]),
    }


@login_required(login_url='/login/')
@allowed_users(roles="Admins")
def client_delete_view(request, pk, **kwargs):

    delete_utility = DeleteObjectsUtil(
        model=Client,
        model_ids=pk,
        order_by='date_created',
        request=request,
        selected_tab='clients-tab'
    )

    context = {}
    if request.method == 'POST':
        form = CheckPasswordForm(request.POST or None,
                                 current_password=request.user.password)
        if form.is_valid():
            delete_utility.delete_objects()
            delete_utility.create_alert()
            return redirect('clients:list')
    else:  # Meaning is a GET request
        form = CheckPasswordForm()
    context = delete_utility.get_context_data()
    context['form'] = form
    client = get_object_or_404(Client, pk=pk)
    context['client'] = client
    context['deposits'] = client.deposit_set.all()
    context['discounts'] = client.discount_set.all()
    return render(request, "clients/delete.html", context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def add_discount_view(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = CreateDiscountForm()
    if request.method == 'POST':
        form = CreateDiscountForm(request.POST)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.created_by = request.user
            discount.client = client
            discount.save()
            partidos = form.cleaned_data['partidos']
            discount.partidos.add(*partidos)
            # partidos_ids = [partido.pk for partido in partidos]
            for disc in Discount.objects.exclude(pk=discount.pk).filter(
                client__id=client.id,
                partidos__in=partidos,
                    is_for_flex=discount.is_for_flex):
                disc.partidos.remove(
                    *disc.partidos.filter(pk__in=[
                        partido.pk for partido in partidos]))
            msg = f'El descuento de {discount.amount}% ' +\
                f'para el cliente {client} se creó correctamente.'
            return create_alert_and_redirect(
                request, msg, 'clients:detail', client.pk)
        else:
            print("INVALIDOOOOOOOOOO")
    context = {
        'form': form,
        'client': client,
        'selected_tab': 'clients-tab',
        'partidos': Partido.objects.all().order_by("name"),
    }
    return render(request, 'clients/add_discount.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def edit_discount_view(request, client_pk, discount_pk):
    client = get_object_or_404(Client, pk=client_pk)
    discount = get_object_or_404(Discount, pk=discount_pk)
    if request.method == 'POST':
        form = CreateDiscountForm(request.POST, instance=discount)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.save()
            partidos = form.cleaned_data['partidos']
            discount.partidos.add(*partidos)
            # partidos_ids = [partido.pk for partido in partidos]
            for disc in Discount.objects.exclude(pk=discount.pk).filter(
                client__id=client.id,
                partidos__in=partidos,
                    is_for_flex=discount.is_for_flex):
                disc.partidos.remove(
                    *disc.partidos.filter(pk__in=[
                        partido.pk for partido in partidos]))
            msg = f'El descuento de {discount.amount}% ' +\
                f'para el cliente {client} se actualizó correctamente.'
            return create_alert_and_redirect(
                request, msg, 'clients:detail', client.pk)
    else:
        form = CreateDiscountForm(instance=discount)
    context = {
        'form': form,
        'client': client,
        'selected_tab': 'clients-tab',
        'partidos': Partido.objects.all().order_by("name"),
        'selected_partidos_ids': discount.partidos.all().values('pk'),
    }
    return render(request, 'clients/edit_discount.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def activate_client_view(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.is_active = True
    client.save()
    msg = (f'El cliente {client} se activó correctamente. '
           'Recordá activar los depósitos y las cuentas '
           'de los usuarios asociados.')
    return create_alert_and_redirect(request, msg, 'clients:detail', client.pk)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def deactivate_client_view(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.is_active = False
    client.save()
    msg = (f'El cliente {client}, sus depósitos y sus usuarios '
           'asociados se desactivaron correctamente.')
    for user in client.client_user_account.all():
        user.is_active = False
        user.save()
    for deposit in client.deposit_set.all():
        deposit.is_active = False
        deposit.save()
    return create_alert_and_redirect(request, msg, 'clients:detail', client.pk)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def delete_discount_view(request, client_pk, discount_pk):
    delete_utility = DeleteObjectsUtil(
        model=Discount,
        model_ids=discount_pk,
        order_by='date_created',
        request=request,
        selected_tab='clients-tab'
    )

    context = {}
    if request.method == 'POST':
        form = CheckPasswordForm(request.POST or None,
                                 current_password=request.user.password)
        if form.is_valid():
            delete_utility.delete_objects()
            delete_utility.create_alert()
            return redirect('clients:detail', client_pk)
    else:  # Meaning is a GET request
        form = CheckPasswordForm()
    context = delete_utility.get_context_data()
    context['form'] = form
    context['client_id'] = client_pk
    discount = get_object_or_404(Discount, pk=discount_pk)
    context['discount'] = discount
    context['partidos'] = discount.partidos.all()
    return render(request, "clients/delete_discount.html", context)
