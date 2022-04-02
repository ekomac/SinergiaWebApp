# Python
from django.conf import settings
import json
from itertools import groupby
from datetime import datetime, timedelta
from typing import Dict, List


# Django
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
from django.http import Http404
from django.http.response import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

# Project
from account.decorators import allowed_users
from account.models import Account
from data.models import Data
from deposit.models import Deposit
from envios.models import Envio
from tracking.models import TrackingMovement


@login_required(login_url='/login/')
def redirect_no_url(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Admins').exists():
            return admin_home_screen_view(request)
        # elif request.user.groups.filter(
        #         name__in=['Level 1', 'Level 2']).exists():
        #     return mobile_based_tracking_actions_view(request)
        elif request.user.groups.filter(name='Clients').exists():
            return redirect(reverse('clients_only:index'))
    return Http404()


# @login_required(login_url='/login/')
# @allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
# def mobile_based_tracking_actions_view(request) -> HttpResponse:
#     """
#     Renders the app's index view.
#     """
#     context = {}
#     is_carrier = request.user.envios_carried_by.count() > 0
#     can_transfer_any = request.user.groups.filter(
#         name__in=["Admins", "Level 1"]).exists()
#     # If user is carrying something, he can transfer it
#     if is_carrier:
#         print("is carrier")
#         context['user_can_transfer'] = True
#     # If user is not carrying anything, he can transfer
#     # anything if he is an admin or a tier 1 employee
#     elif not is_carrier and can_transfer_any:
#         context['user_can_transfer'] = True
#     else:
#         context['user_can_transfer'] = False
#     return render(request, 'baseapp_index.html', context)


# @login_required(login_url='/login/')
# @allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
# def mobile_account_view(request) -> HttpResponse:
#     return render(request, 'baseapp_account.html', {})


@login_required(login_url='/login/')
@allowed_users(roles=settings.ACCESS_EMPLOYEE_APP)
def app_account_change_password_view(request) -> HttpResponse:
    return render(request, 'baseapp_account_change_password.html', {})


@login_required(login_url='/login/')
@allowed_users(roles=["Admins"])
def admin_home_screen_view(request):
    clients_with_envios = get_deposits_with_envios_queryset()
    envios_at_deposit = get_envios_at_deposit()
    carriers_with_envios = get_carriers_with_envios()
    # carriers_with_envios = get_carriers_with_envios_queryset()
    main_stats = {
        'at_origin': Envio.objects.filter(
            status=Envio.STATUS_NEW).count(),
        'at_deposit': Envio.objects.filter(
            status=Envio.STATUS_STILL).count(),
        'moving': Envio.objects.filter(
            status=Envio.STATUS_MOVING).count(),
        'delivered_today': TrackingMovement.objects.filter(
            envios__status=Envio.STATUS_DELIVERED).count(),
    }
    context = {
        'selected_tab': 'home-tab',
        'main_stats': main_stats,
        'clients_with_envios': clients_with_envios,
        'envios_at_deposit': envios_at_deposit,
        'carriers_with_envios': carriers_with_envios,
        'apk_download_url': get_object_or_404(
            Data, key='apk_download_url').value,
    }
    return render(request, 'home.html', context)


def get_deposits_with_envios_queryset() -> QuerySet:
    today = datetime(datetime.now().year,
                     datetime.now().month, datetime.now().day, 23, 59, 59, 99)
    return Deposit.objects.values(
        'id', 'name', 'client__name'
    ).annotate(
        envio_count=Count(
            'envio', filter=Q(
                envio__status=Envio.STATUS_NEW
            )
        ),
        priorities=Count(
            'envio', filter=Q(
                envio__max_delivery_date__lte=today
            )
        ),
        has_special_delivery_schedule_time=Count(
            'envio', filter=Q(
                envio__delivery_schedule__isnull=False
            )
        )
    ).order_by('name')


def get_envios_at_deposit() -> QuerySet:
    return Envio.objects.filter(
        status=Envio.STATUS_STILL,
    ).annotate(
        client_count=Count(
            'client__name'
        ),
    ).order_by()


def get_carriers_with_envios() -> QuerySet:
    return Account.objects.filter(
        envios_carried_by__status=Envio.STATUS_MOVING,
        envios_carried_by__isnull=False,
    ).annotate(
        envio_count=Count(
            'envios_carried_by'
        ),
    ).order_by()


def get_all():
    now = datetime.now()
    today = datetime(now.year, now.month, now.day, 0, 0, 0, 0)
    tomorrow = today + timedelta(days=1)
    moving_envios = Envio.objects.filter(status=Envio.STATUS_MOVING)
    data = []
    for envio in moving_envios:
        carrier = TrackingMovement.objects.filter(
            envios=envio,
            action=TrackingMovement.ACTION_COLLECTION,
            result=TrackingMovement.RESULT_TRANSFERED
        ).last().carrier
        town = envio.town
        data.append([carrier, envio, town])

    data = sorted(data, key=lambda row: row[0].id)
    grouped = [list(g) for _, g in groupby(data, lambda row: row[0])]
    result = {}
    for group in grouped:
        carrier = group[0][0]
        row = {}
        row['carrier'] = carrier
        envios_count = len(group)
        row['envios'] = envios_count
        delivered = len([mov.envios.filter(
            status=Envio.STATUS_DELIVERED
        ).count() for mov in TrackingMovement.objects.filter(
            action=TrackingMovement.ACTION_DELIVERY_ATTEMPT,
            result=TrackingMovement.RESULT_DELIVERED,
            created_by__id=carrier.id,
            date_created__gte=today,
            date_created__lt=tomorrow
        )])
        total = envios_count + delivered
        row['left'] = f'{delivered} de {total} entregados'
        towns = ", ".join(set([item[2].name.title() for item in group]))
        if len(towns) > 50:
            towns = towns[:50] + '...'
        row['towns'] = towns
        result[carrier.id] = row
    return result


def get_carriers_with_envios_queryset() -> Dict[str, List[Envio]]:

    # moving_envios = sorted(list(map(
    #     lambda envio: (
    #         envio, TrackingMovement.objects.filter(
    #             envios=envio,
    #             action=TrackingMovement.ACTION_RECOLECTION,
    #             result=TrackingMovement.RESULT_TRANSFERED
    #         ).last().carrier
    #     ),
    #     list(Envio.objects.filter(status=Envio.STATUS_MOVING))
    # )), key=lambda envio: envio[1].id)
    # moving_envios = sorted(moving_envios, key=lambda envio: envio[1].id)

    # grouped_envios = [list(g) for _, g in groupby(
    #     moving_envios, key=lambda envio: envio[1].id)]
    # for g in grouped_envios:
    # print("g -->", g)
    # print('\n')

    envios = Envio.objects.filter(
        status=Envio.STATUS_MOVING
    ).order_by()
    result = {}
    for envio in envios:
        tracking_movements = TrackingMovement.objects.filter(
            envios=envio, action=TrackingMovement.ACTION_COLLECTION,
            result=TrackingMovement.RESULT_TRANSFERED
        ).order_by('-date_created')
        if tracking_movements:
            carrier = tracking_movements.last().carrier
            key = carrier.id if carrier else -1
            if key in result:
                result[key]['envios'] += 1
                town = envio.town.name.title()
                if town not in result[key]['towns']:
                    result[key]['towns'] += ", " + town
            else:
                result[key] = {
                    'carrier': carrier if key != -1 else "",
                    'envios': 1,
                    'towns': envio.town.name.title()
                }
                if key != -1:
                    # print("No es menos uno")
                    now = datetime.now()
                    today = datetime(
                        now.year, now.month, now.day, 0, 0, 0, 0)
                    tomorrow = today + timedelta(days=1)
                    result[key]['delivered'] = TrackingMovement.objects.filter(
                        action=TrackingMovement.ACTION_DELIVERY_ATTEMPT,
                        result=TrackingMovement.RESULT_DELIVERED,
                        created_by__id=carrier.id,
                        date_created__gte=today,
                        date_created__lt=tomorrow
                    ).count()
            towns = result[key]['towns']
            if len(result[key]['towns']) > 50:
                result[key]['towns'] = towns[:50] + '...'

            # TODO restar delivered de envios
    return result


def map_envio_to_carrier(envio):
    tms = envio.trackingmovement_set.filter(
        action=TrackingMovement.ACTION_COLLECTION,
        result=TrackingMovement.RESULT_TRANSFERED
    )
    if tms.exists():
        if tms.last().carrier:
            return tms.last().carrier
        return ""


def delete_alert_from_session(request, *args, **kwargs):
    """
    This function handles the deletion of alerts troughout the application.
    It is called from an ajax request, and returns the Http response regarding
    the result of the excecution.
    """
    if not request.is_ajax() or not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])
    alerts = request.session.get('alerts', [])
    filtered_alerts = []
    for alert in alerts:
        if alert['id'] != kwargs['id']:
            filtered_alerts.append(alert)
    request.session['alerts'] = filtered_alerts
    return HttpResponse(
        json.dumps({'status': 'ok'}), content_type="application/json"
    )
