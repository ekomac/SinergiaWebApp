from django.urls import path

from .views import (
    envios_view,
    EnvioDetailView,
    # EnviosList,
    EnvioCreate,
    update_envio,
    delete_envio,
    # create_envio_view,
)

app_name = 'envios'
urlpatterns = [
    # ************************* ENVIOS *************************
    path('envio/', envios_view, name="envio-list"),
    path('envio/<int:pk>/', EnvioDetailView.as_view(), name="envio-detail"),
    path('envio/add/', EnvioCreate.as_view(), name="envio-add"),
    path('envio/edit/', update_envio, name="envio-edit"),
    path('envio/delete/', delete_envio, name="envio-delete"),
    # ************************* ENVIOS *************************
]
