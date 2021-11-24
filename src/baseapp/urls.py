from django.urls import path

from .views import (

    # ! BASE INDEX
    app_view,
    central_receive_user_view,

    # ! ORIGIN
    origin_client_view,
    origin_index_view,
    origin_select_all_confirm_view,
    origin_select_id_view,
    origin_select_one_confirm_view,
    origin_select_filter_type_view,
    origin_select_by_filter_view,

    # ! CENTRAL
    central_index_view,
    central_receive_select_all_confirm_view,
    central_receive_select_id_view,
    central_receive_select_one_confirm_view,
    central_receive_select_filter_type_view,
    central_receive_select_by_filter_view,
)

app_name = 'baseapp'
urlpatterns = [


    # ########################## ! BASE INDEX ############################
    path('', app_view, name="index"),
    # ########################## ! BASE INDEX ############################



    # ############################ ! ORIGIN ##############################
    # SELECT CLIENT
    path('origin/', origin_index_view, name="origin-index"),
    # SELECT WHAT TO WITHDRAW
    path('origin/<int:pk>/', origin_client_view, name="origin-client"),
    # WITHDRAW ALL
    path('origin/<int:pk>/confirm-all',
         origin_select_all_confirm_view, name="origin-all"),
    # SELECT FROM SCANNER
    path('origin/<int:pk>/select-id',
         origin_select_id_view, name="origin-select-id"),
    # CONFIRM SELECTED FROM SCANNER
    path('origin/<int:pk>/withdraw',
         origin_select_one_confirm_view, name="origin-selected-id"),
    # SELECT FILTER TYPE TO WITHDRAW
    path('origin/<int:pk>/select-filters', origin_select_filter_type_view,
         name="origin-select-filter-type"),
    # SELECT ITEMS FROM FILTER TO WITHDRAW
    path('origin/<int:pk>/withdraw-many', origin_select_by_filter_view,
         name="origin-select-by-filter"),
    # ############################ ! ORIGIN ##############################



    # ############################ ! CENTRAL ##############################
    # SELECT USER (CARRIER)
    path('central/', central_index_view, name="central-index"),
    # SELECT WHO TO RECEIVE FROM
    path('central/recieve/<int:pk>/', central_receive_user_view,
         name="central-recieve-user"),
    # DEPOSIT ALL
    path('central/recieve/<int:pk>/confirm-all',
         central_receive_select_all_confirm_view, name="central-receive-all"),
    # SELECT FROM SCANNER
    path('central/recieve/<int:pk>/select-id',
         central_receive_select_id_view, name="central-receive-select-id"),
    # CONFIRM SELECTED FROM SCANNER
    path('central/recieve/<int:pk>/withdraw',
         central_receive_select_one_confirm_view,
         name="central-receive-selected-id"),
    # SELECT FILTER TYPE TO CENTRAL DEPOSIT
    path('central/recieve/<int:pk>/select-filters',
         central_receive_select_filter_type_view,
         name="central-receive-select-filter-type"),
    # SELECT ITEMS FROM FILTER TO CENTRAL DEPOSIT
    path('central/recieve/<int:pk>/withdraw-many',
         central_receive_select_by_filter_view,
         name="central-receive-select-by-filter"),
    # ############################ ! CENTRAL ##############################
]
