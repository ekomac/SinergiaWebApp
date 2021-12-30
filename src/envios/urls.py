from django.urls import path

from .views import (
    envios_view,
    EnvioDetailView,
    EnvioCreate,
    bulk_create_envios_view,
    handle_bulk_create_envios_view,
    download_shipment_labels_file_response,
    success_bulk_create_envios_view,
    print_excel_file,
    update_envio,
    delete_envio,
)

app_name = 'envios'
urlpatterns = [

    # ******************************* ENVIOS *******************************
    path('', envios_view, name="envio-list"),
    path('<int:pk>/', EnvioDetailView.as_view(), name="envio-detail"),
    path('add/', EnvioCreate.as_view(), name="envio-add"),
    path('<int:pk>/edit/', update_envio, name="envio-edit"),
    path('<int:pk>/delete/', delete_envio, name="envio-delete"),
    # ******************************* ENVIOS *******************************



    # ******************************* DOWNLAOD *******************************
    path('download/<ids>/', download_shipment_labels_file_response,
         name="envio-download-labels"),
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
