from django.http.response import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
import json


def home_screen_view(request):

    if not request.user.is_authenticated:
        return redirect('login')

    context = {}
    context['selected_tab'] = 'home-tab'
    print(request.user)
    return render(request, 'home.html', context)


def prueba_view(request):

    return render(request, 'prueba.html', {})


def delete_alert_from_session(request, *args, **kwargs):
    if not request.is_ajax() or not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])

    # request.session['alerts'] = []
    alerts = request.session.get('alerts', [])
    filtered_alerts = []
    for alert in alerts:
        if alert['id'] != kwargs['id']:
            filtered_alerts.append(alert)
    request.session['alerts'] = filtered_alerts
    print("se eliminó la alerta con id = ", kwargs['id'])
    return HttpResponse(
        json.dumps({'status': 'ok'}), content_type="application/json"
    )
