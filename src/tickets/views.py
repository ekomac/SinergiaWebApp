# Basic Python
from typing import List, Tuple
from datetime import datetime, timedelta
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
from tickets.forms import CreateTicketForm
from tickets.models import Attachment, Ticket
from utils.alerts.views import delete_alert_and_redirect


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def list_tickets_view(request):

    context = {}

    # Search
    query = ""
    if request.method == "GET":
        query = request.GET.get("query_by", None)
        if query:
            context["query"] = str(query)

        order_by = request.GET.get("order_by", '-date_created')
        if order_by:
            order_by = str(order_by)
            context["order_by"] = order_by
            if '_desc' in order_by:
                order_by = "-" + order_by[:-5]

        results_per_page = request.GET.get("results_per_page", None)
        if results_per_page is None:
            results_per_page = 50
        context['results_per_page'] = str(results_per_page)

        filters = {}
        filter_by = request.GET.get('filter_by', "")
        context['filters_count'] = 0
        if filter_by:
            filters, filter_count = decode_filters(filter_by)
            context['filter_by'] = filter_by
            context['filters_count'] = filter_count

        # Filter tickets
        tickets = get_tickets_queryset(query, order_by, **filters)

        # Pagination
        page = request.GET.get('page', 1)
        tickets_paginator = Paginator(tickets, results_per_page)
        try:
            tickets = tickets_paginator.page(page)
            context['tickets_count'] = tickets_paginator.count
            context['tickets_from'] = tickets_paginator.per_page * \
                (int(page) - 1) + 1
            context['tickets_to'] = context['tickets_from'] + \
                tickets_paginator.per_page - 1
            # print(dir(tickets))
            # print("end_index", tickets.end_index())
            # print("has_next", tickets.has_next())
            # print("has_other_pages", tickets.has_other_pages())
            # print("has_previous", tickets.has_previous())
            # print("next_page_number", tickets.next_page_number())
            # print("number", tickets.number)
            # print("object_list", tickets.object_list)
            # print("paginator count", tickets.paginator.count)
            # print("paginator num_pages", tickets.paginator.num_pages)
            # print("paginator page_range", tickets.paginator.page_range)
            # print("paginator per_page", tickets.paginator.per_page)
            # print("paginator dir", dir(tickets.paginator))
            # print("paginator dict", tickets.paginator.__dict__)
            # print("previous_page_number", tickets.previous_page_number())
            # print("start_index", tickets.start_index())
            # print(tickets.__dict__)
        except PageNotAnInteger:
            tickets = tickets_paginator.page(results_per_page)
        except EmptyPage:
            tickets = tickets_paginator.page(tickets_paginator.num_pages)

        context['tickets'] = tickets
        context['totalTickets'] = len(tickets)
        context['selected_tab'] = 'tickets-tab'
    return render(request, "tickets/list.html", context)


def get_tickets_queryset(
        query: str = None, order_by_key: str = '-date_created',
        **filters) -> List[Ticket]:
    """
    Get all tickets that match provided query, if any. If none is given,
    returns all tickets. Also, performs the query in the specified
    order_by_key.
    Finally, it also filters the query by user driven params, such as, for
    example, 'date_created__gt'.

    Args:
        query (str, optional): words to match the query. Defaults to empyt str.
        order_by_key (str, optional): to perform ordery by.
        Defaults to 'date_created'.
        **filters (Any): filter params to be passed to filter method.

    Returns:
        List[Ticket]: a list containing the tickets which match at least
        one query.
    """
    query = unidecode.unidecode(query) if query else ""
    return list(Ticket.objects
                # User driven filters
                .filter(**filters)
                # Query filters
                .filter(
                    Q(created_by__first_name__contains=query) |
                    Q(created_by__last_name__contains=query) |
                    Q(subject__contains=query) |
                    Q(msg__contains=query) |
                    Q(closed_msg__contains=query),
                )
                .order_by(order_by_key)
                .distinct()
                )


def decode_filters(s: str = '') -> Tuple[dict, int]:
    str_filters = s.split('_')
    filters = {}
    for filter in str_filters:
        key = filter[0]
        value = filter[1:]
        if value:
            if key == 'f':  # The filter is about date created since
                filters['date_created__gte'] = sanitize_date(value)

            if key == 't':  # The filter is about date created until
                filters['date_created__lte'] = sanitize_date(
                    value) + timedelta(days=1)

            if key == 'p':  # The filter is about the priority
                filters['priority'] = value

            if key == 's':  # The filter is about the status
                filters['status'] = value

    return filters, len(filters)


def sanitize_date(s: str) -> datetime:
    """Parses the date given as a string
    "yyyy-mm-dd" to the corresponding date object.

    Args:
        s (str): the date as a string.

    Returns:
        datetime: representing the date.
    """
    parts = s.split('-')
    y = parts[0]
    m = parts[1]
    d = parts[2]
    return datetime(int(y), int(m), int(d))


class CreateTicketView(LoginRequiredMixin, CreateView):

    login_url = '/login/'
    template_name = "tickets/add.html"
    form_class = CreateTicketForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(CreateTicketView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(CreateTicketView, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'tickets-tab'
        return ctx

    def get_success_url(self):
        return reverse('tickets:detail', kwargs={'pk': self.object.pk})

    @ allowed_users_in_class_view(roles=["Admins", "Clients", "EmployeeTier1"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@ login_required(login_url='/login/')
@ allowed_users(roles=["Admins", "EmployeeTier1"])
def ticket_detail_view(request, pk):
    if not request.user.ticket_set.filter(pk=pk).exists():
        return redirect('tickets:list')
    ticket = get_object_or_404(Ticket, pk=pk)
    attachments = Attachment.objects.filter(ticket__id=ticket.id)
    attachments_count = attachments.count()
    context = {
        'ticket': ticket,
        'selected_tab': 'tickets-tab',
        'attachments_count': attachments_count,
        'attachments': [(
            attachment.file.url, truncate_start(attachment.file.url)
        ) for attachment in attachments],
    }
    return render(request, 'tickets/detail.html', context)


def truncate_start(s: str) -> str:
    """Truncates the given string to the last 30 characters.

    Args:
        s (str): the string to be truncated.

    Returns:
        str: the truncated string.
    """
    if '/' in s:
        return ".../" + s[s.rfind('/') + 1:]
    elif len(s) > 30:
        return "..." + s[-30:]
    return s


@ login_required(login_url='/login/')
@ allowed_users(roles=["Admins", "EmployeeTier1"])
def ticket_delete_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        msg = f'El ticket "{ticket}" se eliminó  correctamente.'
        ticket.delete()
        return delete_alert_and_redirect(request, msg, 'tickets:list')
    context = {
        'ticket': ticket,
        'selected_tab': 'tickets-tab'
    }
    return render(request, 'tickets/delete.html', context)
