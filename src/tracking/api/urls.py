
from django.urls import path
from tracking.api.withdraw.views import (
    api_withdraw_all_view,
    api_withdraw_by_envios_ids_view,
    api_withdraw_by_partidos_ids_view,
    api_withdraw_by_towns_ids_view,
    api_withdraw_by_zones_ids_view
)
# from tracking.api.deposit.views import (
#     api_deposit_all_view,
#     api_deposit_by_envios_ids_view,
#     api_deposit_by_towns_ids_view,
#     api_deposit_by_partidos_ids_view,
#     api_deposit_by_zones_ids_view,
# )
from tracking.api.transfer.views import (
    api_transfer_all_view,
    api_transfer_by_envios_ids_view,
    api_transfer_by_towns_ids_view,
    api_transfer_by_partidos_ids_view,
    api_transfer_by_zones_ids_view,
)

app_name = 'tracking'

urlpatterns = [
    path('withdraw/all', api_withdraw_all_view,
         name="api-withdraw-all"),
    path('withdraw/by-envios-ids', api_withdraw_by_envios_ids_view,
         name="api-withdraw-ids"),
    path('withdraw/by-towns-ids', api_withdraw_by_towns_ids_view,
         name="api-withdraw-by-town"),
    path('withdraw/by-partidos-ids', api_withdraw_by_partidos_ids_view,
         name="api-withdraw-by-partido"),
    path('withdraw/by-zones-ids', api_withdraw_by_zones_ids_view,
         name="api-withdraw-by-zone"),

    #     path('deposit/all', api_deposit_all_view,
    #          name="api-deposit-all"),
    #     path('deposit/by-envios-ids', api_deposit_by_envios_ids_view,
    #          name="api-deposit-ids"),
    #     path('deposit/by-towns-ids', api_deposit_by_towns_ids_view,
    #          name="api-deposit-by-town"),
    #     path('deposit/by-partidos-ids', api_deposit_by_partidos_ids_view,
    #          name="api-deposit-by-partido"),
    #     path('deposit/by-zones-ids', api_deposit_by_zones_ids_view,
    #          name="api-deposit-by-zone"),

    path('transfer/all', api_transfer_all_view,
         name="api-transfer-all"),
    path('transfer/by-envios-ids', api_transfer_by_envios_ids_view,
         name="api-transfer-ids"),
    path('transfer/by-towns-ids', api_transfer_by_towns_ids_view,
         name="api-transfer-by-town"),
    path('transfer/by-partidos-ids', api_transfer_by_partidos_ids_view,
         name="api-transfer-by-partido"),
    path('transfer/by-zones-ids', api_transfer_by_zones_ids_view,
         name="api-transfer-by-zone"),

    # path('withdraw/all', api_withdraw_all_view,
    #      name="api-withdraw-all"),
    # path('withdraw/by-envios-ids', api_withdraw_by_envios_ids_view,
    #      name="api-withdraw-ids"),
    # path('withdraw/by-towns-ids', api_withdraw_by_towns_ids_view,
    #      name="api-withdraw-by-town"),
    # path('withdraw/by-partidos-ids', api_withdraw_by_partidos_ids_view,
    #      name="api-withdraw-by-partido"),
    # path('withdraw/by-zones-ids', api_withdraw_by_zones_ids_view,
    #      name="api-withdraw-by-zone"),
]
