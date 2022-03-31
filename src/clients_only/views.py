from django.contrib.auth import views as auth_views
import json
from openpyxl.writer.excel import save_virtual_workbook
import hashlib
from django.http import HttpResponse, JsonResponse
from envios.reports import PDFReport
from envios.utils import (
    bulk_create_envios,
    calculate_price,
    create_xlsx_workbook,
    get_detail_readable
)
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from account.models import Account
from deposit.models import Deposit
from envios.forms import (
    BulkLoadEnviosForm,
    CreateEnvioForm,
    EnviosIdsSelection,
    UpdateEnvioForm
)
from django.views.generic.detail import DetailView
from datetime import datetime, timedelta
from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from account.decorators import allowed_users, allowed_users_in_class_view
from clients.models import Client
from envios.models import BulkLoadEnvios, Envio
from places.models import Partido
from places.utils import get_localidades_as_JSON
from tracking.models import TrackingMovement
from utils.alerts.views import (
    create_alert_and_redirect,
    update_alert_and_redirect)
from utils.forms import CheckPasswordForm

from utils.views import CompleteListView, DeleteObjectsUtil, sanitize_date


class IndexEnvioListView(CompleteListView, LoginRequiredMixin):
    template_name = 'clients_only/list.html'
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

    @allowed_users_in_class_view(roles=["Clients", ])
    def get(self, request):
        if request.user.groups.filter(name='Clients').exists():
            self.base_filters = {
                'client__id': request.user.client.id
            }
        return super(IndexEnvioListView, self).get(request)

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


class EnvioContextMixin(LoginRequiredMixin, View):

    def get_context_data(self, **kwargs):
        ctx = super(EnvioContextMixin, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'shipments-tab'
        return ctx


class EnvioDetailView(EnvioContextMixin, LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = Envio
    template_name = "clients_only/detail.html"

    @allowed_users_in_class_view(roles=["Clients", ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(EnvioDetailView, self).get_context_data(**kwargs)
        envio = ctx['object']
        ctx['movements'] = envio.trackingmovement_set.exclude(
            result=TrackingMovement.RESULT_TRANSFERED).order_by(
            '-date_created')
        ctx['actual_price'] = '{:,.2f}'.format(calculate_price(envio))
        ctx['readable_detail'] = get_detail_readable(envio)
        if envio.status == Envio.STATUS_DELIVERED:
            delivered_tracking_movement = envio.trackingmovement_set.filter(
                result='success').first()
            if delivered_tracking_movement:
                delivered_date = delivered_tracking_movement.date_created
                ctx['delivered_date'] = delivered_date
                deliverer = delivered_tracking_movement.created_by
                ctx['deliverer'] = deliverer
        return ctx


class EnvioCreate(LoginRequiredMixin, CreateView):

    login_url = '/login/'
    template_name = "clients_only/add.html"
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
            self.request, msg, 'clients_only:envio-detail', envio.pk)

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
        elif user.client is not None:
            ctx['initial_client_id'] = user.client.id
        deposit_id = self.request.GET.get('deposit_id', None)
        if deposit_id is not None:
            ctx['initial_deposit_id'] = deposit_id

        return ctx

    def get_success_url(self):
        return reverse('clients_only:envio-detail',
                       kwargs={'pk': self.object.pk})

    @allowed_users_in_class_view(roles=["Admins", "Clients"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@login_required(login_url='/login/')
@allowed_users(roles=["Clients", ])
def edit_envio_view(request, pk):

    envio = get_object_or_404(Envio, pk=pk)
    if envio.status != Envio.STATUS_NEW:
        return redirect('clients_only:envio-detail', pk=pk)
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
                request, msg, 'clients_only:envio-detail', obj.pk)

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
    user = request.user
    # Checks if the user is a client
    is_client = (user.groups.exists()) and (
        user.groups.filter(name__in=["Clients"]).exists()
    ) and (user.client is not None)
    # Sends it to template
    context['is_client'] = is_client

    return render(request, "clients_only/edit.html", context)


@login_required(login_url='/login/')
@allowed_users(roles=["Clients", ])
def cancel_envio_view(request, pk, **kwargs):

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
            delete_utility.objects.update(status=Envio.STATUS_CANCELED)
            movement = TrackingMovement(
                created_by=request.user,
                action=TrackingMovement.ACTION_CANCELLATION,
                result=TrackingMovement.RESULT_CANCELED,
            )
            movement.save()
            movement.envios.add(*delete_utility.objects)
            delete_utility.create_alert(alert_word="canceló")
            return redirect('clients_only:index')
    else:  # Meaning is a GET request
        form = CheckPasswordForm()
    context = delete_utility.get_context_data()
    context['form'] = form
    return render(request, "clients_only/cancel.html", context)


@login_required(login_url='/login/')
@allowed_users(roles=["Clients", ])
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
                return redirect('clients_only:envio-bulk-add-success',
                                pk=obj.pk)
            return redirect('clients_only:bulk-handle', pk=obj.pk)
    context['upload_form'] = form
    context['selected_tab'] = 'shipments-tab'

    # Get params urls to preload client and deposit
    client_id = request.GET.get('client_id', None)
    if client_id is None and request.user.client is not None:
        client_id = request.user.client.id
    if client_id is not None:
        context['initial_client_id'] = client_id
    deposit_id = request.GET.get('deposit_id', None)
    if deposit_id is not None:
        context['initial_deposit_id'] = deposit_id
    context['deposits'] = get_deposits_as_JSON(client_id)
    return render(request, 'clients_only/bulk/add.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Clients", ])
def success_bulk_create_envios_view(request, pk):
    bulk_load = BulkLoadEnvios.objects.get(id=pk)
    if bulk_load.envios_were_created:
        envios = Envio.objects.filter(bulk_upload=bulk_load)
    else:
        envios = bulk_create_envios(bulk_load)
        bulk_load.envios_were_created = True
    bulk_load.load_status = BulkLoadEnvios.LOADING_STATUS_FINISHED
    bulk_load.save()
    ids = "-".join([str(envio.id) for envio in envios])
    context = {'selected_tab': 'shipments-tab', 'ids': ids, 'envios': envios}
    return render(request, 'clients_only/bulk/success.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Clients", ])
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
@allowed_users(roles=["Clients", ])
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
@allowed_users(roles=["Clients", ])
def download_single_shipment_label_file_response(_, pk):
    envios = Envio.objects.filter(id__in=[pk])
    response = HttpResponse(content_type='application/pdf')
    hashed_ids = hashlib.md5(str(pk).encode('utf-8')).hexdigest()
    file_name = 'etiquetas_' + hashed_ids
    response['Content-Disposition'] = f'attachment; filename={file_name}.pdf'
    PDFReport(response).create(envios)
    return response


@login_required(login_url='/login/')
@allowed_users(roles=["Clients", ])
def handle_bulk_create_envios_view(request, pk):
    obj = BulkLoadEnvios.objects.get(id=pk)
    context = {
        'selected_tab': 'shipments-tab',
        'obj': obj,
        'errors': obj.errors.split('\n'),
    }
    return render(request, 'clients_only/bulk/handler.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "Clients"])
def print_excel_file(request, pk):
    obj = BulkLoadEnvios.objects.get(id=pk)
    wb = create_xlsx_workbook(obj.csv_result, obj.cells_to_paint)
    response = HttpResponse(
        save_virtual_workbook(wb), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=result.xlsx'
    return response


def get_deposits_as_JSON(client_id: int = None):
    filters = {'is_active': True, }
    if client_id is not None:
        filters['client_id'] = client_id
    query = Deposit.objects.filter(**filters).order_by('client', 'name')
    mapped = list(map(map_deposit_to_dict, query))
    return json.dumps(mapped)


def map_deposit_to_dict(deposit):
    return {
        'id': deposit.id,
        'name': deposit.full_name().title(),
        'client_id': deposit.client.id if deposit.client else 0,
    }


class CustomPasswordChangeView(auth_views.PasswordChangeView):
    def get_success_url(self):
        return reverse('logout')
