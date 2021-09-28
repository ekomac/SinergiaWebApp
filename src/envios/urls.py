from django.urls import path
from .views import EnvioCreate, EnviosList

app_name = 'envios'
urlpatterns = [
    path('', EnviosList.as_view(), name="envios-list"),
    path('create/', EnvioCreate.as_view(), name="envio-create"),
]
