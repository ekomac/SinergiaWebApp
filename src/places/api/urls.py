from django.urls import path
from places.api.views import (

    ApiTownsAtDepositListView,
    ApiPartidosAtDepositListView,
    ApiZonesAtDepositListView,

    ApiTownsAtCarrierListView,
    ApiPartidosAtCarrierListView,
    ApiZonesAtCarrierListView,

    ApiTownsAtCarrierWithClientFromDepositListView,
    ApiPartidosAtCarrierWithClientFromDepositListView,
)

app_name = 'places-api'

urlpatterns = [
    # AT DEPOSIT
    path(
        'towns-at-deposit/<int:deposit_id>/',
        ApiTownsAtDepositListView.as_view(),
        name="towns-at-deposit"
    ),
    path(
        'partidos-at-deposit/<int:deposit_id>/',
        ApiPartidosAtDepositListView.as_view(),
        name="partidos-at-deposit"
    ),
    path(
        'zones-at-deposit/<int:deposit_id>/',
        ApiZonesAtDepositListView.as_view(),
        name="zones-at-deposit"
    ),

    # AT CARRIER
    path(
        'towns-at-carrier/<int:carrier_id>/',
        ApiTownsAtCarrierListView.as_view(),
        name="towns-at-carrier"
    ),
    path(
        'partidos-at-carrier/<int:carrier_id>/',
        ApiPartidosAtCarrierListView.as_view(),
        name="partidos-at-carrier"
    ),
    path(
        'zones-at-carrier/<int:carrier_id>/',
        ApiZonesAtCarrierListView.as_view(),
        name="zones-at-carrier"
    ),


    # AT CARRIER WITH DEPOSIT
    path(
        'towns-at-carrier-with-deposit/<int:carrier_id>/',
        ApiTownsAtCarrierWithClientFromDepositListView.as_view(),
        name="towns-at-carrier"
    ),
    path(
        'partidos-at-carrier-with-deposit/<int:carrier_id>/',
        ApiPartidosAtCarrierWithClientFromDepositListView.as_view(),
        name="partidos-at-carrier"
    ),
]
