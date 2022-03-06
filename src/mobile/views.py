# Django
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import render

# Project
from account.decorators import allowed_users


@login_required(login_url='/login/')
@allowed_users(roles=['Admins'])
def mobile_based_tracking_actions_view(request) -> HttpResponse:
    """
    Renders the app's index view.
    """
    context = {}
    is_carrier = request.user.envios_carried_by.count() > 0
    can_transfer_any = request.user.groups.filter(
        name__in=["Admins", "Level 1"]).exists()
    # If user is carrying something, he can transfer it
    if is_carrier:
        print("is carrier")
        context['user_can_transfer'] = True
    # If user is not carrying anything, he can transfer
    # anything if he is an admin or a tier 1 employee
    elif not is_carrier and can_transfer_any:
        context['user_can_transfer'] = True
    else:
        context['user_can_transfer'] = False
    return render(request, 'mobile/index.html', context)


@login_required(login_url='/login/')
@allowed_users(roles=['Admins'])
def mobile_account_view(request) -> HttpResponse:
    return render(request, 'mobile/account.html', {})
