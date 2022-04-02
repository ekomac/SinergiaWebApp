from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from account.decorators import allowed_users
from .models import Data


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def download_apk(request):
    url = get_object_or_404(
        Data, key='apk_download_url').value
    return HttpResponseRedirect(url)
