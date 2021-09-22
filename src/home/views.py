from django.shortcuts import redirect, render


def home_screen_view(request):

    if not request.user.is_authenticated:
        return redirect('login')

    context = {}
    print(request.user)
    return render(request, 'base_system.html', context)
