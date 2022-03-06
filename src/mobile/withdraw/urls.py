from django.urls import path
from mobile.withdraw.views import (
    index_view,
    select_carrier_view,
    deposit_view,
    confirm_all_view,
    scan_view,
    confirm_scanned_view,
    filter_by_view,
    confirm_filtered_view
)


app_name = 'mobile-withdraw'


urlpatterns = [

    # SELECT DEPOSIT - FROM WHERE TO WITHDRAW
    path('', index_view, name="index"),

    # SELECT WHO WILL WITHDRAW
    path('<int:deposit_pk>', select_carrier_view, name="select-carrier"),

    # SELECT WHAT TO WITHDRAW (ALL, ONE, FILTERED)
    path('<int:deposit_pk>/to/<int:carrier_pk>',
         deposit_view, name="deposit"),

    # WITHDRAW ALL
    path('<int:deposit_pk>/to/<int:carrier_pk>/confirm-all',
         confirm_all_view, name="confirm-all"),

    # SELECT FROM SCANNER
    path('<int:deposit_pk>/to/<int:carrier_pk>/scan',
         scan_view, name="scan"),

    # CONFIRM SELECTED FROM SCANNER
    path('<int:deposit_pk>/to/<int:carrier_pk>/scan/confirm',
         confirm_scanned_view, name="confirm-scanned"),

    # SELECT FILTER TYPE TO WITHDRAW
    path('<int:deposit_pk>/to/<int:carrier_pk>/filter',
         filter_by_view, name="filter-by"),

    # SELECT ITEMS FROM FILTER TO WITHDRAW
    path('<int:deposit_pk>/to/<int:carrier_pk>/filter/confirm',
         confirm_filtered_view, name="confirm-filtered"),
]
