# Basic Python
import json
import hashlib
import unidecode
from datetime import datetime, timedelta
from django.http.response import HttpResponse
from django.http import JsonResponse
from openpyxl.writer.excel import save_virtual_workbook
from typing import List, Tuple

# Django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from account.decorators import allowed_users, allowed_users_in_class_view


# Project apps
from envios.decorators import allow_only_client_in_class_view
from account.models import Account
from deposit.models import Deposit
from envios.forms import (
    BulkLoadEnviosForm, CreateEnvioForm, EnviosIdsSelection, UpdateEnvioForm)
from envios.models import BulkLoadEnvios, Envio
from envios.utils import bulk_create_envios, create_xlsx_workbook
from places.models import Partido
from clients.models import Client
from envios.reports import PDFReport
from places.utils import get_localidades_as_JSON
from tracking.models import TrackingMovement
from utils.alerts.views import (
    create_alert_and_redirect, update_alert_and_redirect)
from utils.forms import CheckPasswordForm
from utils.views import DeleteObjectsUtil


DEFAULT_ENVIOS_PER_PAGE = 30


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

        results_per_page = request.GET.get(
            'results_per_page', None)
        if results_per_page is None:
            results_per_page = DEFAULT_ENVIOS_PER_PAGE
        context['results_per_page'] = str(results_per_page)

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
        envios_paginator = Paginator(envios, results_per_page)
        try:
            envios = envios_paginator.page(page)
        except PageNotAnInteger:
            envios = envios_paginator.page(results_per_page)
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
                    Q(updated_by__first_name__icontains=query) |
                    Q(updated_by__last_name__icontains=query) |
                    Q(name__icontains=query) |
                    Q(doc__icontains=query) |
                    Q(phone__icontains=query) |
                    Q(street__icontains=query) |
                    Q(remarks__icontains=query) |
                    Q(town__name__icontains=query) |
                    Q(zipcode__icontains=query) |
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

    @allow_only_client_in_class_view
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(EnvioDetailView, self).get_context_data(**kwargs)
        envio = ctx['object']
        ctx['movements'] = envio.trackingmovement_set.all().order_by(
            '-date_created')
        if envio.status == Envio.STATUS_DELIVERED:
            delivered_tracking_movement = envio.trackingmovement_set.filter(
                result='success').first()
            delivered_date = delivered_tracking_movement.date_created
            ctx['delivered_date'] = delivered_date
            deliverer = delivered_tracking_movement.created_by
            ctx['deliverer'] = deliverer
        return ctx


class EnvioCreate(LoginRequiredMixin, CreateView):

    login_url = '/login/'
    template_name = "envios/envio/add.html"
    form_class = CreateEnvioForm

    def form_valid(self, form):
        super(EnvioCreate, self).form_valid(form)
        envio = self.object
        envio.created_by = self.request.user
        envio.save()

        tm = TrackingMovement(
            created_by=self.request.user,
            action=TrackingMovement.ACTION_ADDED_TO_SYSTEM,
            result=TrackingMovement.RESULT_ADDED_TO_SYSTEM,
            deposit=envio.deposit
        )
        tm.save()
        tm.envios.add(*[envio])

        msg = f'El envío "{envio}" se creó correctamente.'
        return create_alert_and_redirect(
            self.request, msg, 'envios:envio-detail', envio.pk)

    def get_context_data(self, **kwargs):
        """
        Overrides default method. If the user is representing a client,
        the form will be pre-filled with the client's deposits and will
        hide the client selection.

        Returns:
            [type]: [description]
        """
        ctx = super(EnvioCreate, self).get_context_data(**kwargs)
        # Gets current user
        user = ctx['view'].request.user

        # Checks if the user is a client
        is_client = (user.groups.exists()) and (
            user.groups.filter(name__in=["Clients"]).exists()
        ) and (user.client is not None)
        # Sends it to template
        ctx['is_client'] = is_client

        if is_client:
            # Gets the client if the user is a client
            client = Client.objects.get(pk=user.client.id)
            # And sends it to template
            ctx['client'] = client
            # Gets the deposit of the client
            # ctx['deposits'] = get_deposits_as_JSON(client_id=user.client.pk)
            ctx['form'].fields['deposit'].queryset = Deposit.objects.filter(
                client__pk=client.pk)
        else:
            # Gets all deposits
            ctx['deposits'] = get_deposits_as_JSON()

        ctx['selected_tab'] = 'shipments-tab'
        ctx['partidos'] = Partido.objects.all().order_by("name")
        ctx['places'] = get_localidades_as_JSON()
        return ctx

    def get_success_url(self):
        return reverse('envios:envio-detail', kwargs={'pk': self.object.pk})

    @allowed_users_in_class_view(roles=["Admins", "Clients"])
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
    context['deposits'] = get_deposits_as_JSON()
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
@allowed_users(roles=["Admins", "Clients"])
def post_selected_ids(request):
    if request.is_ajax and request.method == "POST":
        # get the form data
        form = EnviosIdsSelection(request.POST)
        # save the data and after fetch the object in instance
        if form.is_valid():
            print("is valid")
            ids = form.cleaned_data['ids']
            print(f'{ids=}')
            # serialize in new friend object in json
            # ser_instance = serializers.serialize('json', [ids, ])
            # send to client side.
            request.session['selected-ids-for-download'] = ids
            return JsonResponse({"ids": ids}, status=200)
        else:
            # some form errors occured.
            return JsonResponse({"error": form.errors}, status=400)

    # some error occured
    return JsonResponse({"error": ""}, status=400)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "Clients"])
def download_shipment_labels_file_response(request):
    ids = request.session.get('selected-ids-for-download', None)
    if ids is None:
        return HttpResponse("No ids selected", status=400)
    ids = ids.split('-')
    envios = Envio.objects.filter(id__in=ids)
    response = HttpResponse(content_type='application/pdf')
    hashed_ids = hashlib.md5("".join(ids).encode('utf-8')).hexdigest()
    file_name = 'etiquetas_' + hashed_ids
    response['Content-Disposition'] = f'attachment; filename={file_name}.pdf'
    PDFReport(response).create(envios)
    return response


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "Clients"])
def download_single_shipment_label_file_response(_, pk):
    envios = Envio.objects.filter(id__in=[pk])
    response = HttpResponse(content_type='application/pdf')
    hashed_ids = hashlib.md5(str(pk).encode('utf-8')).hexdigest()
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


def get_deposits_as_JSON(client_id: int = None):
    query = Deposit.objects.all().order_by('client', 'name')
    if client_id is not None:
        query = Deposit.objects.filter(pk=client_id).order_by('client', 'name')
    mapped = list(map(map_deposit_to_dict, query))
    return json.dumps(mapped)


def map_deposit_to_dict(deposit):
    return {
        'id': deposit.id,
        'name': deposit.full_name().title(),
        'client_id': deposit.client.id if deposit.client else 0,
    }


@login_required(login_url='/login/')
@allowed_users(roles="Admins")
def edit_envio_view(request, pk):

    envio = get_object_or_404(Envio, pk=pk)
    if envio.status != Envio.STATUS_NEW:
        return redirect('envios:envio-detail', pk=pk)
    form = UpdateEnvioForm(instance=envio)

    if request.method == 'POST':
        form = UpdateEnvioForm(request.POST or None, instance=envio)

        if form.is_valid():
            obj = form.save()
            obj.updated_by = request.user
            obj.save()
            msg = f'El envío "{obj.full_address()} de {obj.client}" '\
                + 'se actualizó correctamente.'
            return update_alert_and_redirect(
                request, msg, 'envios:envio-detail', obj.pk)

    context = {
        'form': form,
        'envio': envio,
        'deposits': get_deposits_as_JSON(),
        'selected_tab': 'shipments-tab',
        'partidos': Partido.objects.all().order_by("name"),
        'towns': get_localidades_as_JSON(),
        'previuoslySelectedPartidoId': envio.town.partido.id,
        'previuoslySelectedTownId': envio.town.id
    }

    return render(request, "envios/envio/edit.html", context)


@login_required(login_url='/login/')
@allowed_users(roles="Admins")
def delete_envio_view(request, pk, **kwargs):

    delete_utility = DeleteObjectsUtil(
        model=Envio,
        model_ids=pk,
        order_by='date_created',
        request=request,
        selected_tab='envios-tab'
    )

    context = {}
    if request.method == 'POST':
        form = CheckPasswordForm(request.POST or None,
                                 current_password=request.user.password)
        if form.is_valid():
            delete_utility.delete_objects()
            delete_utility.create_alert()
            return redirect('envios:envio-list')
    else:  # Meaning is a GET request
        form = CheckPasswordForm()
    context = delete_utility.get_context_data()
    context['form'] = form
    # context['password_match'] = passwords_match

    return render(request, "envios/envio/delete.html", context)
