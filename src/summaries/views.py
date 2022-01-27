# Python
import csv
import os
from datetime import datetime, timedelta
from typing import Any, Dict

# Django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.http.response import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template

# Thirdparty
from excel_response import ExcelResponse
from xhtml2pdf import pisa

# Project
from account.decorators import allowed_users, allowed_users_in_class_view
from account.models import Account
from clients.models import Client
from summaries.forms import CreateClientSummaryForm, CreateEmployeeSummaryForm
from summaries.models import ClientSummary, EmployeeSummary
from utils.alerts.views import create_alert_and_redirect
from utils.views import CompleteListView, sanitize_date


class ClientSummaryListView(CompleteListView, LoginRequiredMixin):

    template_name = 'summaries/clients/list.html'
    model = ClientSummary
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
    )
    query_keywords = ('client__name', 'client__email', 'client__phone',)
    selected_tab = 'clients-summaries-tab'

    @allowed_users_in_class_view(roles=["Admins"])
    def get(self, request):
        return super(ClientSummaryListView, self).get(request)

    def get_context_data(self) -> Dict[str, Any]:
        context = super().get_context_data()
        context['clients'] = Client.objects.filter(
            envio__isnull=False).distinct()
        return context


class EmployeeSummaryListView(CompleteListView, LoginRequiredMixin):

    template_name = 'summaries/employees/list.html'
    model = EmployeeSummary
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
            'key': 'employee_id',
            'filter': lambda x: 'employee__isnull' if (
                x in [-1, '-1']) else 'employee__id',
            'function': lambda x: True if x in [-1, '-1'] else int(x),
            'context': str,
        },
    )
    query_keywords = (
        'employee__first_name', 'employee__last_name',
        'employee__email', 'employee__phone',
    )
    selected_tab = 'employees-summaries-tab'

    @allowed_users_in_class_view(roles=["Admins"])
    def get(self, request):
        return super(EmployeeSummaryListView, self).get(request)

    def get_context_data(self) -> Dict[str, Any]:
        context = super().get_context_data()
        context['employees'] = Account.objects.filter(
            employee_summary__isnull=False).distinct()
        return context


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def client_summary_create_view(request):
    form = CreateClientSummaryForm()
    if request.method == 'POST':
        print("post", request.POST)
        form = CreateClientSummaryForm(request.POST)
        if form.is_valid():
            summary = form.save(commit=False)
            summary.created_by = request.user
            summary.save()
            msg = f'El resumen "{summary}" se creó correctamente.'
            return create_alert_and_redirect(
                request, msg, 'summaries:client-detail', summary.pk)
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    year = str(yesterday.year).zfill(4)
    month = str(yesterday.month).zfill(2)
    day = str(yesterday.day).zfill(2)

    context = {
        'form': form,
        'selected_tab': 'clients-summaries-tab',
        'max_date': f'{year}-{month}-{day}',
        'summary_type': 'client',
    }
    return render(request, 'summaries/add.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def employee_summary_create_view(request):
    form = CreateEmployeeSummaryForm()
    if request.method == 'POST':
        print("post", request.POST)
        form = CreateEmployeeSummaryForm(request.POST)
        if form.is_valid():
            summary = form.save(commit=False)
            summary.created_by = request.user
            summary.save()
            msg = f'El resumen "{summary}" se creó correctamente.'
            return create_alert_and_redirect(
                request, msg, 'summaries:employee-detail', summary.pk)
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    year = str(yesterday.year).zfill(4)
    month = str(yesterday.month).zfill(2)
    day = str(yesterday.day).zfill(2)

    context = {
        'form': form,
        'selected_tab': 'employees-summaries-tab',
        'max_date': f'{year}-{month}-{day}',
        'summary_type': 'employee',
    }
    return render(request, 'summaries/add.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def client_summary_detail_view(request, pk):
    summary = get_object_or_404(ClientSummary, pk=pk)
    ctx = {'summary': summary, 'selected_tab': 'clients-summaries-tab', }
    return render(request, 'summaries/detail.html', ctx)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def employee_summary_detail_view(request, pk):
    summary = get_object_or_404(EmployeeSummary, pk=pk)
    ctx = {'summary': summary, 'selected_tab': 'employees-summaries-tab', }
    return render(request, 'summaries/detail.html', ctx)


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
        # Typically /static/
        sUrl = settings.STATIC_URL
        # Typically /home/userX/project_static/
        sRoot = settings.STATIC_ROOT
        # Typically /media/
        mUrl = settings.MEDIA_URL
        # Typically /home/userX/project_static/media/
        mRoot = settings.MEDIA_ROOT

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


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def print_csv_summary(request, pk):
    summary = get_object_or_404(ClientSummary, pk=pk)
    rows = ([envio_dict['date_delivered'], envio_dict['destination'],
            envio_dict['detail'], envio_dict['price']
             ] for envio_dict in summary.envios)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    filename = str(summary)
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    return response


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def print_xls_summary(request, pk):
    summary = get_object_or_404(ClientSummary, pk=pk)
    data = [['Fecha de entrega', 'Domicilio', 'Detalle', 'Valor']]
    rows = [[envio_dict['date_delivered'], envio_dict['destination'],
            envio_dict['detail'], envio_dict['price']
             ] for envio_dict in summary.envios]
    data.extend(rows)
    filename = str(summary)
    return ExcelResponse(
        data=data, output_filename=filename, worksheet_name='Reporte')


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def print_pdf_summary(request, pk):
    pass
