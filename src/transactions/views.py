from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from account.decorators import allowed_users

from transactions.forms import CreateTransactionForm, UpdateTransactionForm
from transactions.models import Transaction
from utils.forms import CheckPasswordForm
from utils.views import DeleteObjectsUtil, truncate_start


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def transaction_list_view(request):
    context = {}
    context['selected_tab'] = "transactions-tab"
    transactions = Transaction.objects.all()[:30:-1]
    context['transactions'] = transactions
    return render(request, "transactions/list.html", context)


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
