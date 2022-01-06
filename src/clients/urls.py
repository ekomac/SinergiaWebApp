from django.urls import path

from .views import (
    client_list_view,
    create_client_view,
    edit_client_view,
    client_detail_view,
    client_delete_view,
    add_discount_view
)

app_name = 'clients'
urlpatterns = [
    path('', client_list_view, name="list"),
    path('add/', create_client_view, name="add"),
    path('<int:pk>/', client_detail_view, name="detail"),
    path('<int:pk>/edit/', edit_client_view, name="edit"),
    path('<int:pk>/delete/', client_delete_view, name="delete"),
    path('<int:pk>/add-discount/', add_discount_view, name="add-discount"),
]
