from django.urls import path

from .views import (
    transaction_list_view,
    transaction_create_view,
    transaction_edit_view,
    transaction_detail_view,
    transaction_delete_view
)

app_name = 'transactions'
urlpatterns = [
    path('', transaction_list_view, name="list"),
    path('add/', transaction_create_view, name="add"),
    path('<int:pk>/', transaction_detail_view, name="detail"),
    path('<int:pk>/edit/', transaction_edit_view, name="edit"),
    path('<int:pk>/delete/', transaction_delete_view, name="delete"),
]
