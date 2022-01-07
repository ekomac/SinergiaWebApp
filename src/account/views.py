from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from account.forms import AccountAuthenticationForm


def logout_view(request):
    logout(request)
    return redirect('login')


def login_view(request):

    context = {}
    form = AccountAuthenticationForm()
    if request.user.is_authenticated:
        if request.user.groups.exists() \
                and request.user.groups.filter(
                name__in=["Admins", "Clients"]).exists():
            return redirect('admin-home')
        else:
            return redirect('index')

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                next_url = 'admin-home'
                if user.groups.exists():
                    if user.groups.filter(
                            name__in=['Admins', 'Clients']).exists():
                        next_url = 'admin-home'
                    else:
                        next_url = 'index'
                spec_url = request.GET.get('next', None)
                if spec_url:
                    return redirect(spec_url)
                return redirect(next_url)

    context['login_form'] = form

    return render(request, 'account/login.html', context)


def edit_account_view(request):
    context = {}
    return render(request, 'account/edit.html', context)
