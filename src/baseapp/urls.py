from django.urls import path

from .views import (
    app_view,
    origin_client_view,
    origin_index_view,
    origin_select_all_confirm_view,
    origin_select_ids_view,
    origin_select_filtered_view,
)

app_name = 'baseapp'
urlpatterns = [
    path('', app_view, name="index"),
    path('origin/', origin_index_view, name="origin-index"),
    path('origin/<int:pk>/', origin_client_view, name="origin-client"),
    path('origin/<int:pk>/confirm-all',
         origin_select_all_confirm_view, name="origin-all"),
    path('origin/<int:pk>/select-ids',
         origin_select_ids_view, name="origin-select-ids"),
    path('origin/<int:pk>/select-filters', origin_select_filtered_view,
         name="origin-select-filtered"),
]
