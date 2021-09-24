from django.urls import path
from .views import (
    EnvioCreate,
)

app_name = 'envios'
urlpatterns = [
    path('create/', EnvioCreate.as_view(), name="envio-create"),
]
