from django.urls import path

from .views import (
    DepositListView,
    deposit_create_view,
    deposit_edit_view,
    deposit_detail_view,
    # deposit_delete_view,
    activate_deposit_view,
    deactivate_deposit_view,
)

app_name = 'deposits'
urlpatterns = [
    path('', DepositListView.as_view(), name="list"),
    path('add/', deposit_create_view, name="add"),
    path('<int:pk>/', deposit_detail_view, name="detail"),
    path('<int:pk>/edit/', deposit_edit_view, name="edit"),
    path('<int:pk>/activate/', activate_deposit_view, name="activate"),
    path('<int:pk>/deactivate/', deactivate_deposit_view, name="deactivate"),
    # path('<int:pk>/delete/', deposit_delete_view, name="delete"),
]
