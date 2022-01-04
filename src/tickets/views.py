# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

# Project
from account.decorators import allowed_users


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def list_tickets_view(request):
    ctx = {
        "tickets": request.user.ticket_set.all(),
    }
    return render(request, "tickets/list.html", ctx)


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def ticket_detail_view(request, pk):
    if not request.user.ticket_set.filter(pk).exists():
        return redirect('tickets:list')
    ticket = request.user.ticket_set.get(pk=pk)
    return render(request, 'tickets/detail.html', {'ticket': ticket})


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1"])
def ticket_delete_view(request, pk):
    return render(request, 'tickets/detail.html', {})
