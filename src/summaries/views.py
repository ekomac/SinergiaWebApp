from datetime import datetime, timedelta
from django.conf import settings
import os
from django.contrib.staticfiles import finders
from django.template.loader import get_template
from django.http.response import HttpResponse
import unidecode
from typing import List, Tuple
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

# Thirdparty
from xhtml2pdf import pisa

from account.decorators import allowed_users
from account.utils import get_employees_as_JSON
from clients.utils import get_clients_as_JSON
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
        print("post", request.POST)
        form = CreateSummaryForm(request.POST)
        if form.is_valid():
            summary = form.save(commit=False)
            summary.created_by = request.user
            summary.save()
            msg = f'El resumen "{summary}" se creó correctamente.'
            return create_alert_and_redirect(
                request, msg, 'summaries:detail', summary.pk)
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    year = str(yesterday.year).zfill(4)
    month = str(yesterday.month).zfill(2)
    day = str(yesterday.day).zfill(2)

    context = {
        'form': form,
        'selected_tab': 'summaries-tab',
        'max_date': f'{year}-{month}-{day}',
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


def create_pdf(request):
    ctx = {}
    ctx['nums'] = list(range(0, 500))

    template_path = 'summaries/snippets/client_summary.html'
    context = ctx
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resumen.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path
