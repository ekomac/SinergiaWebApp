# Basic Python
from typing import Dict, List, Tuple
import unidecode

# Django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.edit import CreateView


# Project
from account.decorators import allowed_users, allowed_users_in_class_view
from clients.forms import CreateClientForm
from clients.models import Client, Discount
from deposit.models import Deposit
from places.models import Partido
from tickets.models import Ticket


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def client_list_view(request):

    context = {}

    # Search
    query = ""
    if request.method == "GET":
        query = request.GET.get("query_by", None)
        if query:
            context["query"] = str(query)

        order_by = request.GET.get("order_by", 'name')
        if order_by:
            order_by = str(order_by)
            context["order_by"] = order_by
            if '_desc' in order_by:
                order_by = "-" + order_by[:-5]

        results_per_page = request.GET.get("results_per_page", None)
        if results_per_page is None:
            results_per_page = 30
        context['results_per_page'] = str(results_per_page)

        # Filter clients
        clients = get_tickets_queryset(query, order_by)
        print(clients)

        # Pagination
        page = request.GET.get('page', 1)
        clients_paginator = Paginator(clients, results_per_page)
        try:
            clients = clients_paginator.page(page)
        except PageNotAnInteger:
            clients = clients_paginator.page(results_per_page)
        except EmptyPage:
            clients = clients_paginator.page(clients_paginator.num_pages)

        context['clients'] = clients
        context['totalClients'] = len(clients)
        context['selected_tab'] = 'clients-tab'
    return render(request, "clients/list.html", context)


def get_tickets_queryset(
        query: str = None, order_by_key: str = 'name',
) -> List[Client]:
    """Get all clients that match provided query, if any. If none is given,
    returns all clients. Also, performs the query in the specified
    order_by_key.

    Args:
        query (str, optional): words to match the query. Defaults to empyt str.
        order_by_key (str, optional): to perform ordery by. Defaults to 'name'.

    Returns:
        List[Ticket]: a list containing the envios which match at least
        one query.
    """
    query = unidecode.unidecode(query) if query else ""
    return list(map(map_client_to_tuple, list(
        Client.objects.filter(
            Q(name__contains=query) |
            Q(contact_name__contains=query) |
            Q(contact_phone__contains=query) |
            Q(contact_email__contains=query)
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


class CreateClientView(LoginRequiredMixin, CreateView):

    login_url = '/login/'
    template_name = "clients/add.html"
    form_class = CreateClientForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(CreateClientView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(CreateClientView, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'clients-tab'
        return ctx

    def get_success_url(self):
        return reverse('clients:detail', kwargs={'pk': self.object.pk})

    @allowed_users_in_class_view(roles=["Admins"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EditClientView(LoginRequiredMixin, CreateView):

    login_url = '/login/'
    template_name = "tickets/add.html"
    form_class = CreateClientForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(EditClientView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(EditClientView, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'tickets-tab'
        return ctx

    def get_success_url(self):
        return reverse('tickets:detail', kwargs={'pk': self.object.pk})

    @allowed_users_in_class_view(roles=["Admins", "Clients", "EmployeeTier1"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def client_detail_view(request, pk):
    client = get_object_or_404(Client, pk=pk)
    deposits = Deposit.objects.filter(client__id=client.id)
    deposits_count = deposits.count()
    discounts = Discount.objects.filter(client__id=client.id)
    discounts_count = discounts.count()
    discounts = list(map(map_discount_to_dict, discounts))
    context = {
        'client': client,
        'selected_tab': 'clients-tab',
        'discounts_count': discounts_count,
        'discounts': discounts,
        'deposits_count': deposits_count,
        'deposits': deposits,
        'contract': None,
    }
    if client.contract is not None:
        context['contract'] = truncate_start(client.contract.url)
    return render(request, 'clients/detail.html', context)


def truncate_start(s: str, max_chars: int = 30) -> str:
    """Truncates the given string to the last $max_chars$ characters.

    Args:
        s (str): the string to be truncated.

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
        'type': "Flex" if discount.is_for_flex else "Mensajería",
        'is_for_flex': discount.is_for_flex,
        'amount': discount.amount,
        'partidos': ", ".join(
            [partido.name.title() for partido in discount.partidos.all()]),
    }


def truncate_start(s: str) -> str:
    """Truncates the given string to the last 30 characters.

    Args:
        s(str): the string to be truncated.

    Returns:
        str: the truncated string.
    """
    if '/' in s:
        return ".../" + s[s.rfind('/') + 1:]
    elif len(s) > 30:
        return "..." + s[-30:]
    return s


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def client_delete_view(request, pk):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, pk=pk)
        ticket.delete()
        return redirect('tickets:list')
    context = {
        'ticket': get_object_or_404(Ticket, pk=pk),
        'selected_tab': 'tickets-tab'
    }
    return render(request, 'tickets/delete.html', context)
