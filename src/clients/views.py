# Basic Python
from typing import Any, Dict, List, Tuple
import unidecode

# Django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render


# Project
from account.decorators import allowed_users, allowed_users_in_class_view
from clients.forms import CreateClientForm, CreateDiscountForm, EditClientForm
from clients.models import Client, Discount
from deposit.models import Deposit
from places.models import Partido
from places.utils import get_localidades_as_JSON
from utils.alerts.views import (
    create_alert_and_redirect, update_alert_and_redirect)
from utils.forms import CheckPasswordForm
from utils.views import CompleteListView, DeleteObjectsUtil


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
def client_list_view(request):

    context = {}

    # Search
    query = ""
    if request.method == "GET":
        query = request.GET.get("query_by", None)
        if query:
            context["query_by"] = str(query)

        order_by = request.GET.get("order_by", 'name')
        if order_by:
            order_by = str(order_by)
            context["order_by"] = order_by
            if '_desc' in order_by:
                order_by = "-" + order_by[:-5]

        results_per_page = request.GET.get("results_per_page", None)
        if results_per_page is None:
            results_per_page = 50
        context['results_per_page'] = str(results_per_page)

        # Filter clients
        clients = get_clients_queryset(query, order_by)

        # Pagination
        page = request.GET.get('page', 1)
        clients_paginator = Paginator(clients, results_per_page)
        try:
            clients = clients_paginator.page(page)

            # How many clients in total
            context['clients_count'] = clients_paginator.count

            # Showing client from
            context['clients_from'] = (
                clients.number - 1) * clients_paginator.per_page + 1

            # Showing client to
            if clients_paginator.per_page > len(clients):
                what_to_sum = len(clients)
            else:
                what_to_sum = clients_paginator.per_page
            context['clients_to'] = context['clients_from'] + \
                what_to_sum - 1

        except PageNotAnInteger:
            clients = clients_paginator.page(results_per_page)
        except EmptyPage:
            clients = clients_paginator.page(clients_paginator.num_pages)

        context['clients'] = clients
        context['totalClients'] = len(clients)
        context['selected_tab'] = 'clients-tab'
    return render(request, "clients/list.html", context)


def get_clients_queryset(
        query: str = None, order_by_key: str = 'name',
) -> List[Client]:
    """Get all clients that match provided query, if any. If none is given,
    returns all clients. Also, performs the query in the specified
    order_by_key.

    Args:
        query (str, optional): words to match the query. Defaults to empyt str.
        order_by_key (str, optional): to perform ordery by. Defaults to 'name'.

    Returns:
        List[Client]: a list containing the clients which match at least
        one query.
    """
    query = unidecode.unidecode(query) if query else ""
    return list(map(map_client_to_tuple, list(
        Client.objects.filter(
            Q(name__icontains=query) |
            Q(contact_name__icontains=query) |
            Q(contact_phone__icontains=query) |
            Q(contact_email__icontains=query)
        ).order_by(order_by_key).distinct()
    )))


def map_client_to_tuple(client: Client) -> Tuple[Client, str, int]:
    """
    Maps a client to a tuple containing the client, a str with the deposits
    assigned to it and an int with the number of partidos and towns with
    discounts belonging to it.

    Args:
        client (Client): the client to be mapped.

    Returns:
        Tuple[Client, str, str]: the mapped client, the str with the deposits
        and the number of places with discounts.
    """
    deposits = ", ".join(
        [depo.name for depo in Deposit.objects.filter(client=client)])
    places_with_discounts = Partido.objects.filter(
        discount__client=client).count()
    return (client, deposits, places_with_discounts)


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

    if request.method == 'POST':
        form = EditClientForm(request.POST, request.FILES,
                              instance=Client.objects.get(pk=pk))
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
    ctx = {}
    ctx['client'] = client
    ctx['selected_tab'] = 'clients-tab'
    ctx['discounts_count'] = discounts_count
    ctx['discounts'] = discounts
    ctx['deposits_count'] = deposits_count
    ctx['deposits'] = deposits
    ctx['contract'] = None
    if client.contract:
        ctx['contract'] = {
            'url': client.contract.url,
            'text': truncate_start(client.contract.url),
        }
    return render(request, 'clients/detail.html', ctx)


def truncate_start(s: str, max_chars: int = 30) -> str:
    """Truncates the given string to the last $max_chars$ characters.

    Args:
        s (str): the string to be truncated.
        max_chars (int, optional): the maximum number of characters to be used,
        if the string is longer than this, or if s doesn't contains a '/'.
        Defaults to 30.

    Returns:
        str: the truncated string.
    """
    if '/' in s:
        return ".../" + s[s.rfind('/') + 1:]
    elif len(s) > max_chars:
        return "..." + s[-30:]
    return s


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
