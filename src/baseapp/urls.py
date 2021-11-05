from django.urls import path

from .views import (
    app_view,
    origin_client_view,
    origin_index_view,
    origin_select_all_confirm_view,
    origin_select_specific_view,
    origin_select_some_view,
)

app_name = 'baseapp'
urlpatterns = [
    path('', app_view, name="index"),
    path('origin/', origin_index_view, name="origin-index"),
    path('origin/<int:pk>/', origin_client_view, name="origin-client"),
    path('origin/<int:pk>/confirm-all',
         origin_select_all_confirm_view, name="origin-all"),
    path('origin/<int:pk>/specific/select',
         origin_select_specific_view, name="origin-select-specific"),
    path('origin/<int:pk>/some/select', origin_select_some_view,
         name="origin-select-some"),
]
