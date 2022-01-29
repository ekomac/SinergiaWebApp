
from django.urls import path
from envios.api.views import (
    ApiEnvioListView,
    ApiEnvioListOfCarrierView,
)

app_name = 'envios'

urlpatterns = [
    path('list/', ApiEnvioListView.as_view(), name="list"),
    path('list/carrier/<int:carrier_pk>/',
         ApiEnvioListOfCarrierView.as_view(), name="envios-of-carrier"),
]
