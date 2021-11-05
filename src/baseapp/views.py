from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from account.decorators import allowed_users
from baseapp.forms import WithdrawForm
from clients.models import Client


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
def app_view(request):

    return render(request, 'baseapp/index.html', {})


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def origin_index_view(request):
    context = {}
    form = WithdrawForm()
    if request.method == "POST":
        form = WithdrawForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect("baseapp:index")
    context['withdraw_form'] = form
    return render(request, 'baseapp/origin/index.html', context)
