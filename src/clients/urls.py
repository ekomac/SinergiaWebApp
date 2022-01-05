from django.urls import path

from .views import (
    client_list_view,
    CreateClientView,
    EditClientView,
    client_detail_view,
    client_delete_view
)

app_name = 'clients'
urlpatterns = [

    # ******************************* ENVIOS *******************************
    path('', client_list_view, name="list"),
    path('add/', CreateClientView.as_view(), name="add"),
    path('<int:pk>/', client_detail_view, name="detail"),
    path('<int:pk>/edit/', EditClientView.as_view(), name="edit"),
    path('<int:pk>/delete/', client_delete_view, name="delete"),
]
