
from django.urls import path
from deposit.api.views import (
    ApiDepositListView,
    ApiDepositWithEnviosListView,
    ApiOwnDepositsListView,
    api_detail_deposit_view,
)

app_name = 'deposit-api'

urlpatterns = [
    path('', ApiDepositListView.as_view(), name="list"),
    path('with-envios-list', ApiDepositWithEnviosListView.as_view(),
         name="with-envios-list"),
    path('own', ApiOwnDepositsListView.as_view(),
         name="own"),
    path('<int:pk>/', api_detail_deposit_view, name="detail"),
]
