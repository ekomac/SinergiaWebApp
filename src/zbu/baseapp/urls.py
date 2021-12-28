from django.urls import path

from .views import index
from .views import withdraw
from .views import deposit

app_name = 'baseapp_old'
urlpatterns = [


    # ########################## BASE INDEX ############################
    path('', index.app_view, name="index"),
    # ########################## BASE INDEX ############################



    # ############################ WITHDRAW ##############################
    # SELECT CLIENT
    path('withdraw/', withdraw.index_view, name="withdraw-index"),
    # SELECT WHO WILL WITHDRAW
    path('withdraw/<int:deposit_pk>',
         withdraw.select_carrier_view, name="withdraw-select-carrier"),
    # SELECT FROM WHERE TO WITHDRAW
    path('withdraw/<int:deposit_pk>/to/<int:carrier_pk>',
         withdraw.deposit_view, name="withdraw-deposit"),
    # WITHDRAW ALL
    path('withdraw/<int:deposit_pk>/to/<int:carrier_pk>/confirm-all',
         withdraw.select_all_confirm_view, name="withdraw-all"),
    # SELECT FROM SCANNER
    path('withdraw/<int:deposit_pk>/to/<int:carrier_pk>/scan',
         withdraw.scan_view, name="withdraw-select-id"),
    # CONFIRM SELECTED FROM SCANNER
    path('withdraw/<int:deposit_pk>/to/<int:carrier_pk>/confirm-scanned',
         withdraw.scanned_confirm_view, name="withdraw-selected-id"),
    # SELECT FILTER TYPE TO WITHDRAW
    path('withdraw/<int:deposit_pk>/to/<int:carrier_pk>/select-filters',
         withdraw.select_filter_by_view, name="withdraw-select-filter-type"),
    # SELECT ITEMS FROM FILTER TO WITHDRAW
    path('withdraw/<int:deposit_pk>/to/<int:carrier_pk>/confirm-filtered',
         withdraw.confirm_filtered_view, name="withdraw-select-by-filter"),
    # ############################ WITHDRAW ##############################



    # ############################ DEPOSIT ##############################
    # SELECT CARRIER (USER)
    path('deposit/', deposit.index_view, name="deposit-index"),
    # SELECT WHERE TO DEPOSIT
    path('deposit/<int:carrier_pk>',
         deposit.select_deposit_view, name="deposit-select-deposit"),
    # SELECT WHAT TO DEPOSIT
    path('deposit/<int:carrier_pk>/at/<int:deposit_pk>/', deposit.carrier_view,
         name="deposit-carrier"),
    # DEPOSIT ALL
    path('deposit/<int:carrier_pk>/at/<int:deposit_pk>/confirm-all',
         deposit.select_all_confirm_view, name="deposit-all"),
    # SELECT FROM SCANNER
    path('deposit/<int:carrier_pk>/at/<int:deposit_pk>/scan',
         deposit.select_id_view, name="deposit-select-id"),
    # CONFIRM SELECTED FROM SCANNER
    path('deposit/<int:carrier_pk>/at/<int:deposit_pk>/withdraw',
         deposit.select_one_confirm_view,
         name="deposit-selected-id"),
    # SELECT FILTER TYPE TO DEPOSIT DEPOSIT
    path('deposit/<int:carrier_pk>/at/<int:deposit_pk>/select-filters',
         deposit.select_filter_type_view,
         name="deposit-select-filter-type"),
    # SELECT ITEMS FROM FILTER TO DEPOSIT DEPOSIT
    path('deposit/<int:carrier_pk>/at/<int:deposit_pk>/withdraw-many',
         deposit.select_by_filter_view,
         name="deposit-select-by-filter"),
    # ############################ DEPOSIT ##############################
]
