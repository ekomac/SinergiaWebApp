from django.urls import path

from .views import (
    ChangeListView,
    detail_view
)

app_name = 'changes'
urlpatterns = [
    path('', ChangeListView.as_view(), name="list"),
    path('<int:pk>/', detail_view, name="detail"),
    # path('add/', ChangeCreate.as_view(), name="add"),
    # path('<int:pk>/edit/', edit_envio_view, name="envio-edit"),
    # path('<int:pk>/delete/', delete_envio_view, name="envio-delete"),
]
