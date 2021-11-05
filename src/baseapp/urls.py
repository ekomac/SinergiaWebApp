from django.urls import path

from .views import (
    app_view,
    origin_index_view,
)

app_name = 'baseapp'
urlpatterns = [
    path('', app_view, name="index"),
    path('origin/',
         origin_index_view, name="origin-index"),
]
