# Basic Python
import json
import unidecode
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
from django.views.generic import ListView

# Project apps
from account.models import Account
from envios.bulkutil.extractor import Extractor
from envios.forms import BulkAddForm, CreateEnvioForm
from envios.models import Envio
from places.models import Partido, Town
from clients.models import Client


ENVIOS_PER_PAGE = 30
TIME_FORMAT = '%YYYY%MM%DD'


@login_required(login_url='/login/')
def envios_view(request):
    context = {}

    # Search
    query = ""
    if request.method == 'GET':
        query = request.GET.get('q', None)
        if query:
            context['query'] = str(query)

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


class EnvioContextMixin(View):

    def get_context_data(self, **kwargs):
        ctx = super(EnvioContextMixin, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'shipments-tab'
        return ctx


class EnvioDetailView(EnvioContextMixin, DetailView):
    model = Envio


def download_qr_code_label(request):
    pass


class EnvioCreate(LoginRequiredMixin, CreateView):

    login_url = '/login/'
    template_name = "envios/add.html"
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


@login_required(login_url='/login/')
def bulk_create_envios(request):
    form = BulkAddForm()
    if request.method == 'POST':
        form = BulkAddForm(request.POST or None)
        if form.is_valid():
            client = form.cleaned_data['client']
            file = request.FILES['file']
            extractor = Extractor()
            result, _ = extractor.get_shipments(file)
            print("result", result)
            author = Account.objects.filter(email=request.user.email).first()
            envios = get_envios_from_csv(result, author, client)
            Envio.objects.bulk_create(envios)
    context = {
        'form': form
    }
    return render(request, 'envios/envio/bulk-add.html', context)


class MissingColumn(Exception):
    pass


def get_envios_from_csv(csv_str, author, client):
    """
     0 ID FLEX
     1 DOMICILIO
     2 ENTRECALLES
     3 CODIGO POSTA
     4 LOCALIDAD
     5 PARTIDO
     6 DESTINATARI
     7 DNI DESTINATARIO
     8 TELEFONO DESTINATARIO,
     9 DETALLE DEL ENVIO
    """
    envios = []
    for i, row in enumerate(csv_str.split("\n")):
        if i == 0 or "traking_id" in row:
            print("acá debemos pasar")
            continue
        print("estamos en", i)
        cols = row.split(",")
        kwargs = {}

        if not cols[1]:
            raise MissingColumn(
                f"En la fila {i} no se especificó el domicilio.")

        if not cols[4]:
            raise MissingColumn(
                f"En la fila {i} no se especificó la localidad.")

        if cols[0]:
            kwargs['is_flex'] = True
            kwargs['flex_id'] = cols[0]

        # Adress
        kwargs['recipient_address'] = cols[1]

        # Entrances
        kwargs['recipient_entrances'] = cols[2] if cols[2] else None

        # Zipcode
        kwargs['recipient_zipcode'] = cols[3] if cols[3] else None

        # Town
        towns = Town.objects.filter(name=cols[4].upper())
        print(towns)
        if not towns:
            raise Town.DoesNotExist(f"En la fila {i}, No se encontró la " +
                                    f"localidad con el nombre {cols[4]}")
        # If more than one town with given name,
        # a partido must be specified.
        if len(towns) > 1:
            towns = Town.objects.filter(
                name=cols[4].upper(), partido__name=cols[5].upper())
            if not towns:
                raise Town.DoesNotExist(
                    f"En la fila {i}, se indicó una localidad que " +
                    "pertenece a más de un partido, pero el" +
                    "partido {cols[5]} no se encontró")
        kwargs['recipient_town'] = towns[0]

        # Recipient's Name
        kwargs['recipient_name'] = cols[6] if cols[6] else None

        # Recipient's Doc Id
        kwargs['recipient_doc'] = cols[7] if cols[7] else None

        # Recipient's Phone
        kwargs['recipient_phone'] = cols[8] if cols[8] else None

        # Detail (packages)
        if cols[9]:
            kwargs['detail'] = cols[9]

        kwargs['created_by'] = author
        kwargs['client'] = client

        envios.append(Envio(**kwargs))
    return envios


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


class EnviosList(EnvioContextMixin, ListView):
    model = Envio
    template_name = "envios/list.html"


def update_envio(request):
    return render(request, 'envios/update.html', {})


def delete_envio(request):
    return render(request, 'envios/delete.html', {})
