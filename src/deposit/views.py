from clients.models import Client
from xml.etree.ElementInclude import default_loader
from utils.forms import CheckPasswordForm
from utils.views import DeleteObjectsUtil
from places.utils import get_localidades_as_JSON
from places.models import Partido
from utils.alerts.views import (
    create_alert_and_redirect, update_alert_and_redirect)
import unidecode
from typing import Any, Dict, List, Tuple
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from account.decorators import allowed_users
from deposit.forms import CreateDepositForm
from deposit.models import Deposit
from envios.models import Envio

default_rpp = settings.DEFAULT_RESULTS_PER_PAGE


def str_to_bool(x): return True if x == 'true' else False


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def deposit_list_view(request):

    ctx = {}

    # Search
    query = ""
    if request.method == "GET":
        query = request.GET.get("query_by", None)
        if query:
            ctx["query_by"] = str(query)

        order_by = request.GET.get("order_by", "name")
        if order_by:
            order_by = str(order_by)
            ctx["order_by"] = order_by
            if '_desc' in order_by:
                order_by = "-" + order_by[:-5]

        results_per_page = request.GET.get("results_per_page", None)
        if results_per_page is None:
            results_per_page = 50
        else:
            ctx['results_per_page'] = str(results_per_page)

        filters = {}

        decoders = [
            {
                'key': 'client_id',
                'filter': lambda x: 'client__isnull' if x in [-1, '-1'] else 'client__id',
                'function': lambda x: True if x in [-1, '-1'] else int(x),
                'context': str,
            },
            {
                'key': 'is_active',
                'filter': 'is_active',
                'function': str_to_bool,
                'context': lambda x: x,
            },
            {
                'key': 'has_envios',
                'filter': 'envio__isnull',
                'function': str_to_bool,
                'context': lambda x: x,
            },
        ]

        for decoder in decoders:
            value = request.GET.get(decoder['key'], None)
            if value:
                filter_key_var = decoder['filter']
                filter_key = filter_key_var(value) if callable(
                    filter_key_var) else filter_key_var
                filters[filter_key] = decoder['function'](value)
                ctx[decoder['key']] = decoder['context'](value)

        # client_id = request.GET.get("client_id", None)
        # if client_id is not None:
        #     ctx['client_id'] = str(client_id)
        #     filters['client__id'] = client_id

        # is_active = request.GET.get("is_active", None)
        # if is_active is not None:
        #     ctx['is_active'] = is_active
        #     filters['is_active'] = True if is_active == 'true' else False

        # is_sinergia = request.GET.get("is_sinergia", None)
        # if is_sinergia is not None:
        #     ctx['is_sinergia'] = is_sinergia
        #     filters['is_sinergia'] = True if is_sinergia == 'true' else False

        # has_envios = request.GET.get("has_envios", None)
        # if has_envios is not None:
        #     ctx['has_envios'] = has_envios
        #     filters['has_envios'] = True if has_envios == 'true' else False

        ctx['pagination_base_url'] = get_pagination_base_url(
            query_by=query,
            order_by=ctx["order_by"],
            results_per_page=results_per_page,
            **filters
        )

        # Filter deposits
        deposits = get_deposits_queryset(query, order_by, **filters)

        # Pagination
        page = request.GET.get('page', 1)
        deposits_paginator = Paginator(deposits, results_per_page)
        try:
            deposits = deposits_paginator.page(page)

            # How many deposits in total
            ctx['deposits_count'] = deposits_paginator.count

            # Showing deposit from
            ctx['deposits_from'] = (
                deposits.number - 1) * deposits_paginator.per_page + 1

            # Showing deposit to
            if deposits_paginator.per_page > len(deposits):
                what_to_sum = len(deposits)
            else:
                what_to_sum = deposits_paginator.per_page
            ctx['deposits_to'] = ctx['deposits_from'] + \
                what_to_sum - 1
        except PageNotAnInteger:
            deposits = deposits_paginator.page(results_per_page)
        except EmptyPage:
            deposits = deposits_paginator.page(deposits_paginator.num_pages)

        ctx['deposits'] = deposits
        ctx['clients'] = Client.objects.all()
        ctx['selected_tab'] = 'deposits-tab'
    return render(request, "deposit/list.html", ctx)


def get_deposits_queryset(
    query: str = None,
    order_by_key: str = 'name',
    **filters: Dict[str, Any]
) -> List[Deposit]:
    """Get all deposits that match provided query, if any. If none is given,
    returns all deposits. Also, performs the query in the specified
    order_by_key.

    Args:
        query (str, optional): words to match the query. Defaults to empyt str.
        order_by_key (str, optional): to perform ordery by. Defaults to 'name'.
        filters (Dict[str, Any], optional): filters to apply to the query.

    Returns:
        List[Ticket]: a list containing the deposits which match at least
        one query.
    """
    query = unidecode.unidecode(query) if query else ""
    return list(map(map_deposit_to_tuple, list(
        Deposit.objects.filter(**filters).filter(
            Q(name__icontains=query) |
            Q(client__name__icontains=query) |
            Q(address__icontains=query) |
            Q(town__name__icontains=query)
        ).order_by(order_by_key).distinct()
    )))


def map_deposit_to_tuple(deposit: Deposit) -> Tuple[Deposit, int]:
    """
    Maps a deposit to a tuple containing the deposit and the int with the
    total envios holding.

    Args:
        deposit (Deposit): the deposit to be mapped.

    Returns:
        Tuple[Deposit, int]: the mapped deposit and the int with the total
        envios holding.
    """
    envios_in_deposit = Envio.objects.filter(
        deposit=deposit,
        status__in=[Envio.STATUS_STILL, Envio.STATUS_NEW, ]).count()
    return (deposit, envios_in_deposit)


def get_pagination_base_url(
        query_by: str = "",
        order_by: str = "",
        results_per_page: int = default_rpp,
        **filters
) -> str:

    url = ""
    if query_by is not None and query_by != "":
        url += "query_by=" + query_by + "&"
    if order_by is not None and order_by != "":
        url += "order_by=" + order_by + "&"
    if results_per_page is not None and results_per_page != default_rpp:
        url += "results_per_page=" + str(results_per_page) + "&"
    if filters:
        for key, value in filters.items():
            url += key + "=" + str(value) + "&"
    # if url != "":
        # url = "?" + url[:-1]
        # url = "?" + url
    return url


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def deposit_create_view(request):

    form = CreateDepositForm()
    if request.method == 'POST':
        form = CreateDepositForm(
            request.POST, request.FILES)
        if form.is_valid():
            deposit = form.save()
            deposit.created_by = request.user
            deposit.save()
            msg = f'El depósito "{deposit}" se creó correctamente.'
            return create_alert_and_redirect(
                request, msg, 'deposits:detail', deposit.pk)
    context = {
        'form': form,
        'selected_tab': 'deposits-tab',
        'partidos': Partido.objects.all().order_by("name"),
        'places': get_localidades_as_JSON(),
    }
    return render(request, 'deposit/add.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def deposit_edit_view(request, pk):

    if request.method == 'POST':
        form = CreateDepositForm(request.POST, request.FILES,
                                 instance=Deposit.objects.get(pk=pk))
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.save()
            msg = f'El depósito "{deposit}" se actualizó correctamente.'
            return update_alert_and_redirect(
                request, msg, 'deposits:detail', pk)
    else:
        form = CreateDepositForm(instance=Deposit.objects.get(pk=pk))
    context = {
        'form': form,
        'selected_tab': 'deposits-tab',
        'partidos': Partido.objects.all().order_by("name"),
        'deposit': Deposit.objects.get(pk=pk),
        'places': get_localidades_as_JSON(),
    }
    return render(request, 'deposit/edit.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def deposit_detail_view(request, pk):
    ctx = {}
    deposit = get_object_or_404(Deposit, pk=pk)
    ctx['deposit'] = deposit
    ctx['selected_tab'] = 'deposits-tab'
    ctx['envios'] = Envio.objects.filter(
        deposit__id=deposit.pk, status__in=[
            Envio.STATUS_STILL, Envio.STATUS_NEW]).order_by('-date_created')
    return render(request, 'deposit/detail.html', ctx)


@login_required(login_url='/login/')
@allowed_users(roles="Admins")
def deposit_delete_view(request, pk):

    delete_utility = DeleteObjectsUtil(
        model=Deposit,
        model_ids=pk,
        order_by='name',
        request=request,
        selected_tab='deposits-tab'
    )

    context = {}
    if request.method == 'POST':
        form = CheckPasswordForm(request.POST or None,
                                 current_password=request.user.password)
        if form.is_valid():
            delete_utility.delete_objects()
            delete_utility.create_alert()
            return redirect('deposits:list')
    else:  # Meaning is a GET request
        form = CheckPasswordForm()
    context = delete_utility.get_context_data()
    context['form'] = form
    deposit = get_object_or_404(Deposit, pk=pk)
    context['deposit'] = deposit
    return render(request, "deposit/delete.html", context)
