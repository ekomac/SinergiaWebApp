from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import render

from account.decorators import allowed_users


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "EmployeeTier1", "EmployeeTier2"])
def app_view(request) -> HttpResponse:
    """
    Renders the index view.
    """
    return render(request, 'baseapp/index.html', {})
