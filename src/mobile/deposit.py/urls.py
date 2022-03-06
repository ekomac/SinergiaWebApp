from django.urls import path
from .views import (
    index_view,
    select_deposit_view,
    carrier_view,
    confirm_all_view,
    scan_view,
    confirm_scanned_view,
    filter_by_view,
    confirmed_filtered_view,
)


app_name = 'mobile-deposit'

urlpatterns = [

    # SELECT CARRIER (USER)
    path('', index_view, name="index"),

    # SELECT WHERE TO DEPOSIT
    path('<int:carrier_pk>', select_deposit_view, name="select-deposit"),

    # SELECT WHAT TO DEPOSIT
    path('<int:carrier_pk>/at/<int:deposit_pk>',
         carrier_view, name="carrier"),

    # DEPOSIT ALL
    path('<int:carrier_pk>/at/<int:deposit_pk>/confirm-all',
         confirm_all_view, name="confirm-all"),

    # SELECT FROM SCANNER
    path('<int:carrier_pk>/at/<int:deposit_pk>/scan',
         scan_view, name="scan"),

    # CONFIRM SELECTED FROM SCANNER
    path('<int:carrier_pk>/at/<int:deposit_pk>/scan/confirm',
         confirm_scanned_view, name="confirm-scanned"),

    # SELECT FILTER TYPE TO DEPOSIT DEPOSIT
    path('<int:carrier_pk>/at/<int:deposit_pk>/filter',
         filter_by_view, name="filter-by"),

    # SELECT ITEMS FROM FILTER TO DEPOSIT DEPOSIT
    path('<int:carrier_pk>/at/<int:deposit_pk>/filter/confirm',
         confirmed_filtered_view, name="confirm-filtered"),
]
