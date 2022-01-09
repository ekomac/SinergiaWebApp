import unidecode
from typing import List, Tuple
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from account.decorators import allowed_users
from envios.models import Envio
from summaries.forms import CreateSummaryForm
from summaries.models import Summary
from utils.alerts.views import (
    create_alert_and_redirect,
    delete_alert_and_redirect,
    update_alert_and_redirect)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def summary_list_view(request):

    ctx = {}

    # Search
    query = ""
    if request.method == "GET":
        query = request.GET.get("query_by", None)
        if query:
            ctx["query_by"] = str(query)

        order_by = request.GET.get("order_by", 'date_created_desc')
        if order_by:
            order_by = str(order_by)
            ctx["order_by"] = order_by
            if '_desc' in order_by:
                order_by = "-" + order_by[:-5]

        results_per_page = request.GET.get("results_per_page", None)
        if results_per_page is None:
            results_per_page = 30
        ctx['results_per_page'] = str(results_per_page)

        # Filter summaries
        summaries = get_summaries_queryset(query, order_by)

        # Pagination
        page = request.GET.get('page', 1)
        summaries_paginator = Paginator(summaries, results_per_page)
        try:
            summaries = summaries_paginator.page(page)
        except PageNotAnInteger:
            summaries = summaries_paginator.page(results_per_page)
        except EmptyPage:
            summaries = summaries_paginator.page(summaries_paginator.num_pages)

        ctx['summaries'] = summaries
        ctx['selected_tab'] = 'summaries-tab'
    return render(request, "summaries/list.html", ctx)


def get_summaries_queryset(
        query: str = None, order_by_key: str = '-date_created',
) -> List[Summary]:
    """Get all summaries that match provided query, if any. If none is given,
    returns all summaries. Also, performs the query in the specified
    order_by_key.

    Args:
        query (str, optional): words to match the query. Defaults to empyt str.
        order_by_key (str, optional): to perform ordery by. Defaults to 'name'.

    Returns:
        List[Summary]: a list containing the summaries which match at least
        one query.
    """
    query = unidecode.unidecode(query) if query else ""
    return list(map(map_summary_to_tuple, list(
        Summary.objects.filter(
            Q(client__name__icontains=query) |
            Q(employee__first_name__icontains=query) |
            Q(employee__last_name__icontains=query)
        ).order_by(order_by_key).distinct()
    )))


def map_summary_to_tuple(summary: Summary) -> Tuple[Summary, int]:
    """
    Maps a summary to a tuple containing the summary and the int with the
    total envios holding.

    Args:
        summary (Summary): the client to be mapped.

    Returns:
        Tuple[Summary, int]: the mapped summary and the int with the total
        envios holding.
    """
    print(summary, summary.total_cost)
    envios_in_summary = Envio.objects.filter(
        date_delivered__gte=summary.date_from,
        date_delivered__lte=summary.date_to,
        status__in=[Envio.STATUS_DELIVERED]).count()
    return (summary, envios_in_summary)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def summary_create_view(request):

    form = CreateSummaryForm()
    if request.method == 'POST':
        form = CreateSummaryForm(request.POST)
        if form.is_valid():
            summary = form.save()
            summary.created_by = request.user
            summary.save()
            msg = f'El resumen "{summary}" se creó correctamente.'
            return create_alert_and_redirect(
                request, msg, 'summaries:detail', summary.pk)
    context = {
        'form': form,
        'selected_tab': 'summaries-tab',
    }
    return render(request, 'summaries/add.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def summary_edit_view(request, pk):
    summary = get_object_or_404(Summary, pk=pk)
    if request.method == 'POST':
        form = CreateSummaryForm(
            request.POST, instance=summary)
        if form.is_valid():
            summary = form.save(commit=False)
            summary.save()
            msg = f'El resumen "{summary}" se actualizó correctamente.'
            return update_alert_and_redirect(
                request, msg, 'summaries:detail', pk)
    else:
        form = CreateSummaryForm(instance=summary)
    context = {
        'form': form,
        'selected_tab': 'summaries-tab',
        'summary': summary,
    }
    return render(request, 'summaries/edit.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def summary_detail_view(request, pk):
    ctx = {}
    summary = get_object_or_404(Summary, pk=pk)
    ctx['summary'] = summary
    ctx['selected_tab'] = 'summaries-tab'
    ctx['envios'] = summary.envios_dict
    return render(request, 'summaries/detail.html', ctx)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def summary_delete_view(request, pk):
    summary = get_object_or_404(Summary, pk=pk)
    if request.method == 'POST':
        msg = f'El resumen "{summary}" se eliminó  correctamente.'
        summary.delete()
        return delete_alert_and_redirect(request, msg, 'summaries:list')
    context = {
        'summary': summary,
        'selected_tab': 'tickets-tab'
    }
    return render(request, 'tickets/delete.html', context)
