from django.urls import path
from app_transfer.views import (
    index_view,
    select_receiver_view,
    carrier_view,
    confirm_all_view,
    scan_view,
    confirm_scanned_view,
    filter_by_view,
    confirm_filtered_view
)


app_name = 'app_transfer'


urlpatterns = [

    # SELECT CARRIER - WHO WILL TRANSFER
    path('', index_view, name="index"),

    # SELECT WHO WILL RECEIVE
    path('<int:carrier_pk>', select_receiver_view, name="select-receiver"),

    # SELECT WHAT TO TRANSFER (ALL, ONE, FILTERED)
    path('<int:carrier_pk>/to/<int:receiver_pk>',
         carrier_view, name="carrier"),

    # TRANSFER ALL
    path('<int:carrier_pk>/to/<int:receiver_pk>/confirm-all',
         confirm_all_view, name="confirm-all"),

    # SELECT FROM SCANNER
    path('<int:carrier_pk>/to/<int:receiver_pk>/scan', scan_view, name="scan"),

    # CONFIRM SELECTED FROM SCANNER
    path('<int:carrier_pk>/to/<int:receiver_pk>/scan/confirm',
         confirm_scanned_view, name="confirm-scanned"),

    # SELECT FILTER TYPE TO TRANSFER
    path('<int:carrier_pk>/to/<int:receiver_pk>/filter',
         filter_by_view, name="filter-by"),

    # SELECT ITEMS FROM FILTER TO TRANSFER
    path('<int:carrier_pk>/to/<int:receiver_pk>/filter/confirm',
         confirm_filtered_view, name="confirm-filtered"),
]
