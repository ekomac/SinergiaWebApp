from django.urls import path
from clients.api.views import ApiClientsAtDepositListView

app_name = 'clients-api'

urlpatterns = [
    path(
        'clients-at-deposit/<int:deposit_id>/',
        ApiClientsAtDepositListView.as_view(),
        name="towns-at-deposit"
    ),
]
