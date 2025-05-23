from django.urls import path

from .views import (
    EnvioListView,
    #     envios_view,
    EnvioDetailView,
    EnvioCreate,
    bulk_create_envios_view,
    handle_bulk_create_envios_view,
    post_selected_ids,
    download_single_shipment_label_file_response,
    download_shipment_labels_file_response,
    download_envios_list,
    download_envios_list_by_employee,
    print_empty_excel_file,
    success_bulk_create_envios_view,
    print_excel_file,
    # update_envio,
    edit_envio_view,
    delete_envio_view,
    withdraw_envio_view,
    deposit_envio_view,
    transfer_envio_view,
    devolver_envio_view,
    delivery_attempt_envio_view,
    successful_delivery_envio_view,
)

app_name = 'envios'
urlpatterns = [

    # ******************************* ENVIOS *******************************
    path('', EnvioListView.as_view(), name="envio-list"),
    path('<int:pk>/', EnvioDetailView.as_view(), name="envio-detail"),
    path('add/', EnvioCreate.as_view(), name="envio-add"),
    path('<int:pk>/edit/', edit_envio_view, name="envio-edit"),
    path('<int:pk>/delete/', delete_envio_view, name="envio-delete"),
    path('<int:pk>/withdraw/', withdraw_envio_view, name="envio-withdraw"),
    path('<int:pk>/deposit/', deposit_envio_view, name="envio-deposit"),
    path('<int:pk>/transfer/', transfer_envio_view, name="envio-transfer"),
    path('<int:pk>/devolver/', devolver_envio_view, name="envio-devolver"),
    path('<int:pk>/delivery-attempt/', delivery_attempt_envio_view,
         name="envio-delivery-attempt"),
    path('<int:pk>/successful-delivery/', successful_delivery_envio_view,
         name="envio-successful-delivery"),
    # ******************************* ENVIOS *******************************



    # ******************************* DOWNLAOD *******************************
    path('post_ids/', post_selected_ids, name="post-selected-ids"),
    path('download/<int:pk>/', download_single_shipment_label_file_response,
         name="single-envio-download-label"),
    path('download/', download_shipment_labels_file_response,
         name="envio-download-labels"),
    path('download/list/selected', download_envios_list,
         name="envio-download-list"),
    path('download/list/by_employee/<int:employee_pk>',
         download_envios_list_by_employee,
         name="envio-download-employee-list"),
    path('print-empty-xlsx/', print_empty_excel_file,
         name="print-empty-xlsx"),
    # ******************************* DOWNLAOD *******************************

    # ******************************* BULK *******************************
    path('bulk-add/', bulk_create_envios_view, name="envio-bulk-add"),
    path('bulk-add/<int:pk>/success/', success_bulk_create_envios_view,
         name="envio-bulk-add-success"),
    path('bulk-add/<int:pk>/fix/',
         handle_bulk_create_envios_view, name="bulk-handle"),
    path('bulk-add/download-excel-to-fix/<int:pk>/', print_excel_file,
         name="bulk-download-fix-excel"),
    # ******************************* BULK *******************************
]
