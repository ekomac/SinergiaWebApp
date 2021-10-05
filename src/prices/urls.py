from django.urls import path

from .views import (
    codes_view,
)

app_name = 'prices'
urlpatterns = [
    path('', codes_view, name="list"),
    # path('<int:pk>/', , name="detail"),
    # path('add/', , name="create"),
    # path('edit/', , name="edit"),
    # path('delete/', , name="delete"),
]
