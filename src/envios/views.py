# Basic Python
import json
import hashlib
import unidecode
from openpyxl.writer.excel import save_virtual_workbook
from django.http.response import HttpResponse
from datetime import datetime, timedelta
from typing import List, Tuple

# Django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.query_utils import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from account.decorators import allowed_users, allowed_users_in_class_view


# Project apps
from account.models import Account
from envios.forms import BulkLoadEnviosForm, CreateEnvioForm
from envios.models import BulkLoadEnvios, Envio, TrackingMovement
from envios.utils import bulk_create_envios, create_xlsx_workbook
from places.models import Partido, Town
from clients.models import Client
from envios.reports import PDFReport


ENVIOS_PER_PAGE = 30
TIME_FORMAT = '%YYYY%MM%DD'


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def envios_view(request):
    context = {}

    # Search
    query = ""
    if request.method == 'GET':
        query = request.GET.get('query_by', None)
        if query:
            context['query_by'] = str(query)

        order_by = request.GET.get('order_by', '-date_created')
        if order_by:
            order_by = str(order_by)
            context['order_by'] = order_by
            if '_desc' in order_by:
                order_by = "-" + order_by[:-5]

        filters = {}
        filter_by = request.GET.get('filter_by', "")
        context['filters_count'] = 0
        if filter_by:
            filters, filter_count = decode_filters(filter_by)
            context['filter_by'] = filter_by
            context['filters_count'] = filter_count

        envios = get_envio_queryset(
            query, order_by, **filters)

        # Pagination
        page = request.GET.get('page', 1)
        envios_paginator = Paginator(envios, ENVIOS_PER_PAGE)
        try:
            envios = envios_paginator.page(page)
        except PageNotAnInteger:
            envios = envios_paginator.page(ENVIOS_PER_PAGE)
        except EmptyPage:
            envios = envios_paginator.page(envios_paginator.num_pages)

        context['envios'] = envios
        context['totalEnvios'] = len(envios)
        context['selected_tab'] = 'shipments-tab'
        context['clients'] = Client.objects.all()

    return render(request, "envios/envio/list.html", context)


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

            if key == 'c':  # The filter is about the client
                filters['client__id'] = int(value)

            # The filter is about the type of shipment (flex or delivery)
            # The database query is composed in the form of 'is_flex=[bool]',
            # so we need a bool
            if key == 's':
                filters['is_flex'] = value == 'flex'

            if key == 'u':
                filters['shipment_status'] = value

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


def get_envio_queryset(
        query: str = None, order_by_key: str = '-date_created',
        **filters) -> List[Envio]:
    """Get all envios that match provided query, if any. If none is given,
    returns all envios. Also, performs the query in the specified order_by_key.
    Finally, it also filters the query by user driven params, such as, for
    example, 'date_created__gt'.

    Args:
        query (str, optional): words to match the query. Defaults to empyt str.
        order_by_key (str, optional): to perform ordery by.
        Defaults to 'date_created'.
        **filters (Any): filter params to be passed to filter method.

    Returns:
        List[Envio]: a list containing the envios which match at least
        one query.
    """
    query = unidecode.unidecode(query) if query else ""
    return list(Envio.objects
                # User driven filters
                .filter(**filters)
                # Query filters
                .filter(
                    Q(created_by__first_name__icontains=query) |
                    Q(created_by__last_name__icontains=query) |
                    Q(recipient_name__icontains=query) |
                    Q(recipient_doc__icontains=query) |
                    Q(recipient_phone__icontains=query) |
                    Q(recipient_address__icontains=query) |
                    Q(recipient_entrances__icontains=query) |
                    Q(recipient_town__name__icontains=query) |
                    Q(recipient_zipcode__icontains=query) |
                    Q(client__name__icontains=query) |
                    Q(flex_id__icontains=query),
                )
                .order_by(order_by_key)
                .distinct()
                )


class EnvioContextMixin(LoginRequiredMixin, View):

    def get_context_data(self, **kwargs):
        ctx = super(EnvioContextMixin, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'shipments-tab'
        return ctx


class EnvioDetailView(EnvioContextMixin, LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = Envio
    template_name = "envios/envio/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tracking_movements = TrackingMovement.objects.filter(
            Q()
        )
        context['tracking_movements'] = tracking_movements
        return context


class EnvioCreate(LoginRequiredMixin, CreateView):

    login_url = '/login/'
    template_name = "envios/envio/add.html"
    form_class = CreateEnvioForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(EnvioCreate, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'shipments-tab'
        ctx['partidos'] = Partido.objects.all().order_by("name")
        ctx['places'] = get_localidades_as_JSON()
        return ctx

    def get_success_url(self):
        return reverse('envios:envio-detail', kwargs={'pk': self.object.pk})

    @allowed_users_in_class_view(roles=["Admins"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def bulk_create_envios_view(request):
    context = {}
    form = BulkLoadEnviosForm()
    if request.method == 'POST':
        user = Account.objects.get(email=request.user.email)
        form = BulkLoadEnviosForm(
            user, request.POST or None, request.FILES or None)
        if form.is_valid():
            obj = form.save()
            if not obj.requires_manual_fix and not obj.errors:
                return redirect('envios:envio-bulk-add-success', pk=obj.pk)
            return redirect('envios:bulk-handle', pk=obj.pk)
    context['upload_form'] = form
    context['selected_tab'] = 'shipments-tab'
    return render(request, 'envios/bulk/add.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def success_bulk_create_envios_view(request, pk):
    bulk_load = BulkLoadEnvios.objects.get(id=pk)
    envios = bulk_create_envios(bulk_load)
    bulk_load.load_status = BulkLoadEnvios.LOADING_STATUS_FINISHED
    bulk_load.save()
    ids = "-".join([str(envio.id) for envio in envios])
    context = {'selected_tab': 'shipments-tab', 'ids': ids, 'envios': envios}
    return render(request, 'envios/bulk/success.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def download_shipment_labels_file_response(_, ids):
    ids = ids.split('-')
    envios = Envio.objects.filter(id__in=ids)
    response = HttpResponse(content_type='application/pdf')
    hashed_ids = hashlib.md5("".join(ids).encode('utf-8')).hexdigest()
    file_name = 'etiquetas_' + hashed_ids
    response['Content-Disposition'] = f'attachment; filename={file_name}.pdf'
    PDFReport(response).create(envios)
    return response


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def handle_bulk_create_envios_view(request, pk):
    obj = BulkLoadEnvios.objects.get(id=pk)
    context = {
        'selected_tab': 'shipments-tab',
        'obj': obj,
        'errors': obj.errors.split('\n'),
    }
    return render(request, 'envios/bulk/handler.html', context)


@login_required(login_url='/login/')
def print_excel_file(request, pk):
    obj = BulkLoadEnvios.objects.get(id=pk)
    wb = create_xlsx_workbook(obj.csv_result, obj.cells_to_paint)
    response = HttpResponse(
        save_virtual_workbook(wb), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=result.xlsx'
    return response


class MissingColumn(Exception):
    pass


def get_localidades_as_JSON():
    query = Town.objects.all().order_by('name')
    mapped = list(map(map_town_to_dict, query))
    return json.dumps(mapped)


def map_town_to_dict(town):
    return {
        'id': town.id,
        'name': town.name.title(),
        'partido_id': town.partido.id,
    }


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def create_envio_view(request):

    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    form = CreateEnvioForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        created_by = Account.objects.filter(email=user.email).first()
        obj.created_by = created_by
        obj.save()
        form = CreateEnvioForm()

    context['form'] = form

    return render(request, "envios/create.html", context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def update_envio(request):
    return render(request, 'envios/update.html', {})


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def delete_envio(request):
    return render(request, 'envios/delete.html', {})
