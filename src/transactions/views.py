import csv
from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from excel_response import ExcelResponse
from account.decorators import allowed_users, allowed_users_in_class_view

from transactions.forms import CreateTransactionForm, UpdateTransactionForm
from transactions.models import Transaction
from transactions.util.pdf import PDFTransactionsReport
from transactions.util.xlsx import parse_transaction_to_list
from utils.forms import CheckPasswordForm
from utils.views import (
    CompleteListView,
    DeleteObjectsUtil,
    sanitize_date,
    truncate_start
)


class TransactionsListView(CompleteListView, LoginRequiredMixin):

    template_name = 'transactions/list.html'
    model = Transaction
    decoders = (
        {
            'key': 'min_date',
            'filter': 'date__gte',
            'function': sanitize_date,
            'context': lambda x: x,
        },
        {
            'key': 'max_date',
            'filter': 'date__lte',
            'function': lambda x: sanitize_date(x, True) + timedelta(days=1),
            'context': lambda x: x,
        },
        {
            'key': 'category',
            'filter': lambda x: 'category__isnull' if (
                x in [-1, '-1']) else 'category',
            'function': lambda x: True if x in [-1, '-1'] else int(x),
            'context': str,
        },
    )
    query_keywords = ('description',)
    selected_tab = 'transactions-tab'

    @allowed_users_in_class_view(roles=["Admins"])
    def get(self, request):
        return super(TransactionsListView, self).get(request)

    def get_context_data(self) -> Dict[str, Any]:
        context = super().get_context_data()
        context['categories'] = Transaction.CATEGORIES
        return context


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def transaction_create_view(request):
    context = {}
    context['selected_tab'] = "transactions-tab"
    form = CreateTransactionForm()
    if request.method == 'POST':
        form = CreateTransactionForm(
            request.POST or None, request.FILES or None)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.created_by = request.user
            transaction.save()
            return redirect('transactions:list')
    context['form'] = form
    context['edit_mode'] = False

    now = datetime.now()
    year = str(now.year).zfill(4)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)

    context['max_date'] = f'{year}-{month}-{day}'
    return render(request, "transactions/add.html", context)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def transaction_edit_view(request, pk):
    context = {}
    context['selected_tab'] = "transactions-tab"
    transaction = get_object_or_404(Transaction, pk=pk)
    context['transaction'] = transaction
    form = UpdateTransactionForm(instance=transaction)

    now = datetime.now()
    year = str(now.year).zfill(4)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)

    context['max_date'] = f'{year}-{month}-{day}'

    if transaction.proof_of_payment:
        context['proof_of_payment'] = {
            'url': transaction.proof_of_payment.url,
            'text': truncate_start(transaction.proof_of_payment.url),
        }

    if request.method == 'POST':
        form = UpdateTransactionForm(
            request.POST or None, request.FILES or None, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('transactions:list')
    context['form'] = form
    context['edit_mode'] = True
    return render(request, "transactions/edit.html", context)


@login_required(login_url='/login/')
@allowed_users(roles="Admins")
def transaction_delete_view(request, pk, **kwargs):

    delete_utility = DeleteObjectsUtil(
        model=Transaction,
        model_ids=pk,
        order_by='date_created',
        request=request,
        selected_tab='transactions-tab'
    )

    context = {}
    if request.method == 'POST':
        form = CheckPasswordForm(
            request.POST or None,
            current_password=request.user.password
        )
        if form.is_valid():
            delete_utility.delete_objects()
            delete_utility.create_alert()
            return redirect('transactions:list')
    else:  # Meaning is a GET request
        form = CheckPasswordForm()
    context = delete_utility.get_context_data()
    context['form'] = form
    # context['password_match'] = passwords_match

    return render(request, "transactions/delete.html", context)


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def print_csv(request):
    date_from = sanitize_date(request.GET.get('date_from'), True)
    date_to = sanitize_date(request.GET.get('date_to'), True)
    filename = "Transacciones desde %s hasta %s.pdf" % (
        date_from.strftime('%Y-%m-%d'), date_to.strftime('%Y-%m-%d'))
    transactions = list(Transaction.objects.filter(
        date__gte=date_from,
        date__lte=date_to
    ))
    rows = [['Fecha', 'Categoria', 'Descripcion', 'Importe']]
    rows.extend([parse_transaction_to_list(transaction)
                 for transaction in transactions])
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    return response


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def print_xlsx(request):
    date_from = sanitize_date(request.GET.get('date_from'), True)
    date_to = sanitize_date(request.GET.get('date_to'), True)
    filename = "Transacciones desde %s hasta %s.pdf" % (
        date_from.strftime('%Y-%m-%d'), date_to.strftime('%Y-%m-%d'))
    transactions = list(Transaction.objects.filter(
        date__gte=date_from,
        date__lte=date_to
    ))
    data = [['Fecha', 'Categoria', 'Descripcion', 'Importe']]
    rows = [parse_transaction_to_list(transaction)
            for transaction in transactions]
    data.extend(rows)
    return ExcelResponse(
        data=data, output_filename=filename, worksheet_name='Reporte')


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def print_pdf(request):
    date_from = sanitize_date(request.GET.get('date_from'), True)
    date_to = sanitize_date(request.GET.get('date_to'), True)
    pdf_name = "Transacciones desde %s hasta %s.pdf" % (
        date_from.strftime('%Y-%m-%d'), date_to.strftime('%Y-%m-%d'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="%s.pdf"' % pdf_name)
    transactions = list(Transaction.objects.filter(
        date__gte=date_from,
        date__lte=date_to
    ))
    print(transactions)
    buffer = BytesIO()
    pdf = PDFTransactionsReport(buffer, transactions, date_from, date_to)
    pdf.create()
    response.write(buffer.getvalue())
    buffer.close()
    return response
