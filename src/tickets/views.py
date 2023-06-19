# Basic Python
from typing import List, Tuple
from datetime import datetime, timedelta
from django.http import JsonResponse
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
from account.decorators import (
    allowed_users,
    allowed_users_in_class_view,
    only_superusers_allowed
)
from account.models import Account
from tickets.forms import AddAttachmentsToTicketForm, CreateTicketForm
from tickets.models import Attachment, Ticket, TicketMessage
from utils.alerts.views import delete_alert_and_redirect


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "Level 1"])
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

        if not request.user.is_superuser:
            filters['created_by'] = request.user

        # Filter tickets
        tickets = get_tickets_queryset(query, order_by, **filters)

        # Pagination
        page = request.GET.get('page', 1)
        tickets_paginator = Paginator(tickets, results_per_page)
        try:
            tickets = tickets_paginator.page(page)

            # How many tickets in total
            context['tickets_count'] = tickets_paginator.count

            # Showing ticket from
            context['tickets_from'] = (
                tickets.number - 1) * tickets_paginator.per_page + 1

            # Showing ticket to
            if tickets_paginator.per_page > len(tickets):
                what_to_sum = len(tickets)
            else:
                what_to_sum = tickets_paginator.per_page
            context['tickets_to'] = context['tickets_from'] + \
                what_to_sum - 1
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

    @allowed_users_in_class_view(roles=["Admins", "Clients", "Level 1"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "Level 1"])
def ticket_detail_view(request, pk):
    if not request.user.is_superuser:
        if not request.user.tickets_created.filter(pk=pk).exists():
            return redirect('tickets:list')

    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == "POST":
        form = AddAttachmentsToTicketForm(request.POST, request.FILES)

        def to_html_txt(attachment: Attachment):
            url = attachment.file.url
            truncated = truncate_start(attachment.file.url)
            return f'<li><a href="{url}">{truncated}</a></li>'

        attachments = form.save(ticket_id=ticket.pk)
        attachments = ''.join(map(to_html_txt, attachments))

        msg = f"Acá van estos archivos:<br><ul>{attachments}</ul>"
        ticket_message = TicketMessage(
            created_by=request.user, msg=msg, ticket=ticket)
        ticket_message.save()

    attachments = Attachment.objects.filter(ticket__id=ticket.id)
    attachments_count = attachments.count()
    chats = TicketMessage.objects.filter(ticket__id=ticket.id)
    context = {
        'ticket': ticket,
        'selected_tab': 'tickets-tab',
        'attachments_count': attachments_count,
        'attachments': [(
            attachment.file.url, truncate_start(attachment.file.url)
        ) for attachment in attachments],
        'chats': chats
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
        return ".../" + truncate_get_params(s[s.rfind('/') + 1:])
    elif len(s) > 30:
        return "..." + truncate_get_params(s[-30:])
    return s


def truncate_get_params(s: str) -> str:
    if '?' in s:
        i = s.index('?')
        return s[:i]
    return s


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "Level 1"])
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


@login_required(login_url='/login/')
@only_superusers_allowed()
def open_ticket_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    ticket.status = '2'
    ticket.save()
    return redirect('tickets:detail', pk=ticket.pk)


@login_required(login_url='/login/')
@only_superusers_allowed()
def ajax_close_ticket_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        closed_reason = request.POST.get('closed_reason', '')
        closed_msg = request.POST.get('closed_message', '')
        ticket.status = '3'
        ticket.closed_reason = closed_reason
        ticket.closed_msg = closed_msg
        ticket.closed_by = request.user
        ticket.save()
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({"nothing to see": "this isn't happening"})


@login_required(login_url='/login/')
@only_superusers_allowed()
def ajax_cancel_ticket_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        closed_reason = request.POST.get('closed_reason', '')
        closed_msg = request.POST.get('closed_msg', '')
        ticket.status = '3'
        ticket.closed_reason = closed_reason
        ticket.closed_msg = closed_msg
        ticket.closed_by = request.user
        ticket.save()
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({"nothing to see": "this isn't happening"})


AJAX_POST_SUCCESS_CHAT_ITEM = """
<div class="card mt-3">
    <div class="card-header px-2 py-1 d-flex justify-content-between">
        <div class="d-flex flex-row">
            <div><a href="{author_detail_url}">{author_full_name}</a></div>
            <div class="text-muted">&nbsp;dijo:</div>
        </div>
        <div class="text-muted">El {date_created} a las {hour_created}</div>
    </div>
    <div class="card-body p-2">{msg}</div>
</div>
"""


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", ])
def ajax_post_message(request, ticket_pk, user_pk, ):
    ticket = get_object_or_404(Ticket, pk=ticket_pk)
    user = get_object_or_404(Account, pk=user_pk)
    if request.method == 'POST':
        msg = TicketMessage(ticket=ticket, created_by=user,
                            msg=request.POST.get('post-msg', ''))
        msg.save()
        return JsonResponse({'newItem': AJAX_POST_SUCCESS_CHAT_ITEM.format(
            author_detail_url=reverse(
                'account:employees-detail', kwargs={'pk': user.pk}),
            author_full_name=user.full_name,
            date_created=msg.date_created.strftime('%d/%m/%Y'),
            hour_created=msg.date_created.strftime('%H:%M'),
            msg=msg.msg
        )})
    else:
        return JsonResponse({"nothing to see": "this isn't happening"})


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", ])
def cancel_ticket_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    ticket.status = '3'
    ticket.closed_reason = '1'
    ticket.closed_msg = 'Cancelado por usuario autor del ticket'
    ticket.closed_by = request.user
    ticket.save()
    return redirect('tickets:detail', pk=ticket.pk)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", ])
def mark_resolved_ticket_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    ticket.status = '3'
    ticket.closed_reason = '4'
    ticket.closed_msg = 'Marcado como resuelto por usuario autor del ticket'
    ticket.closed_by = request.user
    ticket.save()
    return redirect('tickets:detail', pk=ticket.pk)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", ])
def change_priority_ticket_view(request, pk, priority):
    # Update ticket
    ticket = get_object_or_404(Ticket, pk=pk)
    ticket.priority = priority
    ticket.save()
    msg = ("Se actualizó la prioridad del ticket.")

    # Create ticket message to notify user
    ticket_message = TicketMessage(
        created_by=request.user,
        msg=msg,
        ticket=ticket,
        is_priority_update=True
    )
    ticket_message.save()
    return redirect('tickets:detail', pk=ticket.pk)
