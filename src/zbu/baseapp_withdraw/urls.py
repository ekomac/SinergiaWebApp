from django.urls import path
from .views import (
    index_view,
    select_carrier_view,
    deposit_view,
    select_all_confirm_view,
    scan_view,
    scanned_confirm_view,
    select_filter_by_view,
    confirm_filtered_view
)


app_name = 'baseapp_withdraw'


urlpatterns = [
    # SELECT CLIENT
    path('', index_view, name="withdraw-index"),
    # SELECT WHO WILL WITHDRAW
    path('<int:deposit_pk>',
         select_carrier_view, name="withdraw-select-carrier"),
    # SELECT FROM WHERE TO WITHDRAW
    path('<int:deposit_pk>/to/<int:carrier_pk>',
         deposit_view, name="withdraw-deposit"),
    # WITHDRAW ALL
    path('<int:deposit_pk>/to/<int:carrier_pk>/confirm-all',
         select_all_confirm_view, name="withdraw-all"),
    # SELECT FROM SCANNER
    path('<int:deposit_pk>/to/<int:carrier_pk>/scan',
         scan_view, name="withdraw-select-id"),
    # CONFIRM SELECTED FROM SCANNER
    path('<int:deposit_pk>/to/<int:carrier_pk>/confirm-scanned',
         scanned_confirm_view, name="withdraw-selected-id"),
    # SELECT FILTER TYPE TO WITHDRAW
    path('<int:deposit_pk>/to/<int:carrier_pk>/select-filters',
         select_filter_by_view, name="withdraw-select-filter-type"),
    # SELECT ITEMS FROM FILTER TO WITHDRAW
    path('<int:deposit_pk>/to/<int:carrier_pk>/confirm-filtered',
         confirm_filtered_view, name="withdraw-select-by-filter"),
]
