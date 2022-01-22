from django.urls import path
from places.api.views import (
    ApiTownsOfEnviosInDepositListView,
)

app_name = 'places-api'

urlpatterns = [
    path(
        'towns-of-envios-in-deposit',
        ApiTownsOfEnviosInDepositListView.as_view(),
        name="towns-of-envios-in-deposit-list"
    ),
]
