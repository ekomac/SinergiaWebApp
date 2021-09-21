from django.shortcuts import render


def home_screen_view(request):
    context = {}
    print(request.user)
    return render(request, 'base.html', context)
