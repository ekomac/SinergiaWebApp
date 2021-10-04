from django.shortcuts import redirect, render


def home_screen_view(request):

    if not request.user.is_authenticated:
        return redirect('login')

    context = {}
    context['selected_tab'] = 'home-tab'
    print(request.user)
    return render(request, 'home.html', context)


def prueba_view(request):

    return render(request, 'prueba.html', {})
