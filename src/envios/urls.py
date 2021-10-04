from django.urls import path

from .views import (
    EnvioDetailView,
    EnviosList,
    EnvioCreate,
    update_envio,
    delete_envio,
    # create_envio_view,
)

app_name = 'envios'
urlpatterns = [
    path('', EnviosList.as_view(), name="list"),
    path('<int:pk>/', EnvioDetailView.as_view(), name="detail"),
    path('add/', EnvioCreate.as_view(), name="create"),
    path('edit/', update_envio, name="edit"),
    path('delete/', delete_envio, name="delete"),
]
