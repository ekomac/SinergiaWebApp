from django.urls import path

from .views import (
    TownDetailView,
    towns_view,
)

app_name = 'places'
urlpatterns = [
    path('', towns_view, name="towns-list"),
    path('<int:pk>/', TownDetailView.as_view(), name="town-detail"),
    # path('add/', EnvioCreate.as_view(), name="create"),
    # path('edit/', update_envio, name="edit"),
    # path('delete/', delete_envio, name="delete"),
]
