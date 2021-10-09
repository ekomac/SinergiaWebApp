from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from account.forms import AccountAuthenticationForm


def logout_view(request):
    logout(request)
    return redirect('home')


def login_view(request):

    context = {}

    if request.user.is_authenticated:
        return redirect('home')

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                next_url = 'home'
                spec_url = request.GET.get('next', '')
                if spec_url and spec_url != '':
                    return redirect(spec_url)
                return redirect(next_url)

    else:
        form = AccountAuthenticationForm()

    context['login_form'] = form

    return render(request, 'account/login.html', context)


def edit_account_view(request):
    context = {}
    return render(request, 'account/edit.html', context)
