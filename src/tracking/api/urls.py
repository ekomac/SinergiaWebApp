
from django.urls import path
from tracking.api.deliver.views import (
    api_delivery_attempt_view,
    api_post_successfull_delivery_view
)
from tracking.api.deposit.views import (
    api_deposit_all_view,
    api_deposit_by_envios_ids_view,
    api_deposit_by_towns_ids_view,
    api_deposit_by_partidos_ids_view,
    api_deposit_by_zones_ids_view,
    api_envios_for_deposit_preview,
)
from tracking.api.devolver.views import (
    api_devolver_all_view,
    api_devolver_by_envios_ids_view,
    api_devolver_by_towns_ids_view,
    api_devolver_by_partidos_ids_view,
    api_envios_for_devolver_preview,
)
from tracking.api.summary.views import TrackingMovementsForCarrierListView
from tracking.api.transfer.views import (
    api_transfer_all_view,
    api_transfer_by_envios_ids_view,
    api_transfer_by_towns_ids_view,
    api_transfer_by_partidos_ids_view,
    api_transfer_by_zones_ids_view,
    api_envios_for_transfer_preview,
)
from tracking.api.withdraw.views import (
    api_withdraw_all_view,
    api_withdraw_by_envios_ids_view,
    api_withdraw_by_partidos_ids_view,
    api_withdraw_by_towns_ids_view,
    api_withdraw_by_zones_ids_view,
    api_withdraw_by_clients_ids_view,
    api_envios_for_withdraw_preview,
)

app_name = 'tracking'

urlpatterns = [

    path('withdraw/all/', api_withdraw_all_view,
         name="api-withdraw-all"),

    path('withdraw/by-tracking-envios-ids/', api_withdraw_by_envios_ids_view,
         name="api-withdraw-ids"),

    path('withdraw/by-towns-ids/', api_withdraw_by_towns_ids_view,
         name="api-withdraw-by-town"),

    path('withdraw/by-partidos-ids/', api_withdraw_by_partidos_ids_view,
         name="api-withdraw-by-partido"),

    path('withdraw/by-zones-ids/', api_withdraw_by_zones_ids_view,
         name="api-withdraw-by-zone"),

    path('withdraw/by-clients-ids/', api_withdraw_by_clients_ids_view,
         name="api-withdraw-by-clients"),

    path('withdraw/preview/', api_envios_for_withdraw_preview,
         name="api-withdraw-preview"),



    path('deposit/all/', api_deposit_all_view,
         name="api-deposit-all"),

    path('deposit/by-envios-ids/', api_deposit_by_envios_ids_view,
         name="api-deposit-ids"),

    path('deposit/by-towns-ids/', api_deposit_by_towns_ids_view,
         name="api-deposit-by-town"),

    path('deposit/by-partidos-ids/', api_deposit_by_partidos_ids_view,
         name="api-deposit-by-partido"),

    path('deposit/by-zones-ids/', api_deposit_by_zones_ids_view,
         name="api-deposit-by-zone"),

    path('deposit/preview/', api_envios_for_deposit_preview,
         name="api-deposit-preview"),



    path('devolver/all/', api_devolver_all_view,
         name="api-devolver-all"),

    path('devolver/by-envios-ids/', api_devolver_by_envios_ids_view,
         name="api-devolver-ids"),

    path('devolver/by-towns-ids/', api_devolver_by_towns_ids_view,
         name="api-devolver-by-town"),

    path('devolver/by-partidos-ids/', api_devolver_by_partidos_ids_view,
         name="api-devolver-by-partido"),

    path('devolver/preview/', api_envios_for_devolver_preview,
         name="api-devolver-preview"),


    path('transfer/all/', api_transfer_all_view,
         name="api-transfer-all"),

    path('transfer/by-envios-ids/', api_transfer_by_envios_ids_view,
         name="api-transfer-ids"),

    path('transfer/by-towns-ids/', api_transfer_by_towns_ids_view,
         name="api-transfer-by-town"),

    path('transfer/by-partidos-ids/', api_transfer_by_partidos_ids_view,
         name="api-transfer-by-partido"),

    path('transfer/by-zones-ids/', api_transfer_by_zones_ids_view,
         name="api-transfer-by-zone"),

    path('transfer/preview/', api_envios_for_transfer_preview,
         name="api-transfer-preview"),


    path('deliver/attempt/', api_delivery_attempt_view,
         name="api-delivery-attempt"),

    path('deliver/success/', api_post_successfull_delivery_view,
         name="api-post-successfull-delivery"),


    path('summary/<int:carrier_pk>/',
         TrackingMovementsForCarrierListView.as_view(),
         name="tracking-summary-list"),
]
