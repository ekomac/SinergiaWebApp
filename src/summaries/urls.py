from django.urls import path

from .views import (
    summary_list_view,
    summary_create_view,
    summary_edit_view,
    summary_detail_view,
    summary_delete_view
)

app_name = 'summaries'
urlpatterns = [
    path('', summary_list_view, name="list"),
    path('add/', summary_create_view, name="add"),
    path('<int:pk>/', summary_detail_view, name="detail"),
    path('<int:pk>/edit/', summary_edit_view, name="edit"),
    path('<int:pk>/delete/', summary_delete_view, name="delete"),
]
