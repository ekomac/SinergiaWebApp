from django.urls import path
from baseapp_deposit.views import (
    index_view,
    select_deposit_view,
    carrier_view,
    select_all_confirm_view,
    select_id_view,
    select_one_confirm_view,
    select_filter_type_view,
    select_by_filter_view,
)


app_name = 'app_deposit'

urlpatterns = [
    # SELECT CARRIER (USER)
    path('', index_view, name="deposit-index"),
    # SELECT WHERE TO DEPOSIT
    path('<int:carrier_pk>',
         select_deposit_view, name="deposit-select-deposit"),
    # SELECT WHAT TO DEPOSIT
    path('<int:carrier_pk>/at/<int:deposit_pk>/', carrier_view,
         name="deposit-carrier"),
    # DEPOSIT ALL
    path('<int:carrier_pk>/at/<int:deposit_pk>/confirm-all',
         select_all_confirm_view, name="deposit-all"),
    # SELECT FROM SCANNER
    path('<int:carrier_pk>/at/<int:deposit_pk>/scan',
         select_id_view, name="deposit-select-id"),
    # CONFIRM SELECTED FROM SCANNER
    path('<int:carrier_pk>/at/<int:deposit_pk>/withdraw',
         select_one_confirm_view,
         name="deposit-selected-id"),
    # SELECT FILTER TYPE TO DEPOSIT DEPOSIT
    path('<int:carrier_pk>/at/<int:deposit_pk>/select-filters',
         select_filter_type_view,
         name="deposit-select-filter-type"),
    # SELECT ITEMS FROM FILTER TO DEPOSIT DEPOSIT
    path('<int:carrier_pk>/at/<int:deposit_pk>/withdraw-many',
         select_by_filter_view,
         name="deposit-select-by-filter"),
]
