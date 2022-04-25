# Basic Python
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict

# Third-party
from openpyxl.writer.excel import save_virtual_workbook


# Django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

# Project apps
from account.decorators import allowed_users, allowed_users_in_class_view
from account.models import Account
from clients.models import Client
from deposit.models import Deposit
from envios.forms import (
    ActionDeliveryAttemptForm,
    ActionDepositForm,
    ActionDevolverForm,
    ActionSuccessfulDeliveryForm,
    ActionTransferForm,
    ActionWithdrawForm,
    BulkLoadEnviosForm,
    CreateEnvioForm,
    EnviosIdsSelection,
    UpdateEnvioForm
)
from envios.models import BulkLoadEnvios, Envio
from envios.reports import PDFReport
from envios.utils import (
    bulk_create_envios,
    calculate_price,
    create_empty_xlsx_workbook,
    create_xlsx_workbook,
    get_detail_readable
)
from places.models import Partido
from places.utils import get_localidades_as_JSON
from tracking.models import TrackingMovement
from utils.alerts.views import (
    create_alert_and_redirect,
    update_alert_and_redirect
)
from utils.forms import CheckPasswordForm
from utils.views import DeleteObjectsUtil, CompleteListView, sanitize_date


class EnvioListView(CompleteListView, LoginRequiredMixin):
    template_name = 'envios/envio/list.html'
    model = Envio
    decoders = (
        {
            'key': 'min_date',
            'filter': 'date_created__gte',
            'function': sanitize_date,
            'context': lambda x: x,
        },
        {
            'key': 'max_date',
            'filter': 'date_created__lte',
            'function': lambda x: sanitize_date(x, True) + timedelta(days=1),
            'context': lambda x: x,
        },
        {
            'key': 'client_id',
            'filter': lambda x: 'client__isnull' if (
                x in [-1, '-1']) else 'client__id',
            'function': lambda x: True if x in [-1, '-1'] else int(x),
            'context': str,
        },
        {
            'key': 'status',
            'filter': 'status',
            'function': lambda x: x,
            'context': lambda x: x,
        },
        {
            'key': 'is_flex',
            'filter': 'is_flex',
            'function': lambda x: True if x == 'true' else False,
            'context': lambda x: x,
        },
    )
    query_keywords = (
        'updated_by__first_name__icontains',
        'updated_by__last_name__icontains',
        'name__icontains',
        'doc__icontains',
        'phone__icontains',
        'street__icontains',
        'remarks__icontains',
        'town__name__icontains',
        'zipcode__icontains',
        'client__name__icontains',
    )

    @allowed_users_in_class_view(roles=["Admins"])
    def get(self, request):
        return super(EnvioListView, self).get(request)

    def get_context_data(self) -> Dict[str, Any]:
        context = super().get_context_data()
        context['clients'] = Client.objects.all()
        context['selected_tab'] = 'shipments-tab'
        now = datetime.now()
        year = str(now.year).zfill(4)
        month = str(now.month).zfill(2)
        day = str(now.day).zfill(2)
        context['max_selectable_date'] = f'{year}-{month}-{day}'
        return context


DEFAULT_ENVIOS_PER_PAGE = 50


class EnvioContextMixin(LoginRequiredMixin, View):

    def get_context_data(self, **kwargs):
        ctx = super(EnvioContextMixin, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'shipments-tab'
        return ctx


class EnvioDetailView(EnvioContextMixin, LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = Envio
    template_name = "envios/envio/detail.html"

    @allowed_users_in_class_view(roles=["Admins", ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(EnvioDetailView, self).get_context_data(**kwargs)
        envio = ctx['object']
        ctx['movements'] = envio.trackingmovement_set.all().order_by(
            '-date_created')
        ctx['actual_price'] = '{:,.2f}'.format(calculate_price(envio))
        ctx['readable_detail'] = get_detail_readable(envio)
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

        # Get params urls to preload client and deposit
        client_id = self.request.GET.get('client_id', None)
        if client_id is not None:
            ctx['initial_client_id'] = client_id
        deposit_id = self.request.GET.get('deposit_id', None)
        if deposit_id is not None:
            ctx['initial_deposit_id'] = deposit_id

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

    # Get params urls to preload client and deposit
    client_id = request.GET.get('client_id', None)
    if client_id is not None:
        context['initial_client_id'] = client_id
    deposit_id = request.GET.get('deposit_id', None)
    if deposit_id is not None:
        context['initial_deposit_id'] = deposit_id

    return render(request, 'envios/bulk/add.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def success_bulk_create_envios_view(request, pk):
    bulk_load: BulkLoadEnvios = BulkLoadEnvios.objects.get(id=pk)
    if bulk_load.envios_were_created:
        envios = Envio.objects.filter(bulk_upload=bulk_load)
    else:
        envios, unused_flex_ids = bulk_create_envios(bulk_load)
        bulk_load.unused_flex_ids = ", ".join(unused_flex_ids)
        bulk_load.envios_were_created = True
    bulk_load.load_status = BulkLoadEnvios.LOADING_STATUS_FINISHED
    bulk_load.save()
    ids = "-".join([str(envio.id) for envio in envios])
    context = {
        'selected_tab': 'shipments-tab',
        'ids': ids,
        'envios': envios,
        'unused_flex_ids': bulk_load.unused_flex_ids
    }
    return render(request, 'envios/bulk/success.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "Clients"])
def post_selected_ids(request):
    if request.is_ajax and request.method == "POST":
        # get the form data
        form = EnviosIdsSelection(request.POST)
        # save the data and after fetch the object in instance
        if form.is_valid():
            ids = form.cleaned_data['ids']
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
@allowed_users(roles=["Admins", "Clients"])
def print_excel_file(request, pk):
    obj = BulkLoadEnvios.objects.get(id=pk)
    wb = create_xlsx_workbook(obj.csv_result, obj.cells_to_paint)
    response = HttpResponse(
        save_virtual_workbook(wb), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=result.xlsx'
    return response


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "Clients"])
def print_empty_excel_file(request):
    wb = create_empty_xlsx_workbook()
    response = HttpResponse(
        save_virtual_workbook(wb), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=modelo.xlsx'
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
@allowed_users(roles=["Admins", "Clients"])
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
            msg = f'El envío "{obj.full_address} de {obj.client}" '\
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
        'previuoslySelectedTownId': envio.town.id,
        'is_flex': envio.is_flex
    }
    user = request.user
    # Checks if the user is a client
    is_client = (user.groups.exists()) and (
        user.groups.filter(name__in=["Clients"]).exists()
    ) and (user.client is not None)
    # Sends it to template
    context['is_client'] = is_client

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


def withdraw_envio_view(request, pk: int):
    envio = get_object_or_404(Envio, pk=pk)
    form = ActionWithdrawForm(user=request.user, envio=envio)
    if request.method == 'POST':
        form = ActionWithdrawForm(
            data=request.POST, user=request.user, envio=envio)
        if form.is_valid():
            movement = form.perform_action()
            print(movement)
            msg = f'El envío "{envio.full_address} de {envio.client}" '\
                + 'se retiró correctamente.'
            return update_alert_and_redirect(
                request, msg, 'envios:envio-detail', envio.pk)
    context = {
        'form': form,
        'envio': envio,
        'selected_tab': 'shipments-tab',
    }
    return render(request, "envios/envio/actions/withdraw.html", context)


def deposit_envio_view(request, pk: int):
    envio = get_object_or_404(Envio, pk=pk)
    form = ActionDepositForm(user=request.user, envio=envio)
    if request.method == 'POST':
        form = ActionDepositForm(
            data=request.POST, user=request.user, envio=envio)
        if form.is_valid():
            movement = form.perform_action()
            print(movement)
            msg = f'El envío "{envio.full_address} de {envio.client}" '\
                + 'se depositó correctamente.'
            return update_alert_and_redirect(
                request, msg, 'envios:envio-detail', envio.pk)
    context = {
        'form': form,
        'envio': envio,
        'selected_tab': 'shipments-tab',
    }
    return render(request, "envios/envio/actions/deposit.html", context)


def transfer_envio_view(request, pk: int):
    envio = get_object_or_404(Envio, pk=pk)
    form = ActionTransferForm(user=request.user, envio=envio)
    if request.method == 'POST':
        form = ActionTransferForm(
            data=request.POST, user=request.user, envio=envio)
        if form.is_valid():
            movement = form.perform_action()
            print(movement)
            msg = f'El envío "{envio.full_address} de {envio.client}" '\
                + 'se transferió correctamente.'
            return update_alert_and_redirect(
                request, msg, 'envios:envio-detail', envio.pk)
    context = {
        'form': form,
        'envio': envio,
        'selected_tab': 'shipments-tab',
    }
    return render(request, "envios/envio/actions/transfer.html", context)


def devolver_envio_view(request, pk: int):
    envio = get_object_or_404(Envio, pk=pk)
    form = ActionDevolverForm(user=request.user, envio=envio)
    if request.method == 'POST':
        form = ActionDevolverForm(
            data=request.POST, user=request.user, envio=envio)
        if form.is_valid():
            movement = form.perform_action()
            print(movement)
            msg = f'El envío "{envio.full_address} de {envio.client}" '\
                + 'se devolvió correctamente.'
            return update_alert_and_redirect(
                request, msg, 'envios:envio-detail', envio.pk)
    context = {
        'form': form,
        'envio': envio,
        'selected_tab': 'shipments-tab',
    }
    return render(request, "envios/envio/actions/devolver.html", context)


def delivery_attempt_envio_view(request, pk: int):
    envio = get_object_or_404(Envio, pk=pk)
    form = ActionDeliveryAttemptForm(user=request.user, envio=envio)
    if request.method == 'POST':
        form = ActionDeliveryAttemptForm(
            data=request.POST, user=request.user, envio=envio)
        if form.is_valid():
            movement = form.perform_action()
            print(movement)
            msg = f'El envío "{envio.full_address} de {envio.client}" '\
                + 'se intentó entregar correctamente.'
            return update_alert_and_redirect(
                request, msg, 'envios:envio-detail', envio.pk)
    context = {
        'form': form,
        'envio': envio,
        'selected_tab': 'shipments-tab',
    }
    return render(
        request, "envios/envio/actions/delivery_attempt.html", context)


def successful_delivery_envio_view(request, pk: int):
    envio = get_object_or_404(Envio, pk=pk)
    form = ActionSuccessfulDeliveryForm(user=request.user, envio=envio)
    if request.method == 'POST':
        form = ActionSuccessfulDeliveryForm(
            data=request.POST, user=request.user, envio=envio)
        if form.is_valid():
            movement = form.perform_action()
            print(movement)
            msg = f'El envío "{envio.full_address} de {envio.client}" '\
                + 'se entregó correctamente.'
            return update_alert_and_redirect(
                request, msg, 'envios:envio-detail', envio.pk)
    context = {
        'form': form,
        'envio': envio,
        'selected_tab': 'shipments-tab',
    }
    return render(
        request, "envios/envio/actions/successful_delivery.html", context)
