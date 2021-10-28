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
    path('envio/', envios_view, name="envio-list"),
    path('envio/<int:pk>/', EnvioDetailView.as_view(), name="envio-detail"),
    path('envio/add/', EnvioCreate.as_view(), name="envio-add"),
    path('envio/edit/', update_envio, name="envio-edit"),
    path('envio/delete/', delete_envio, name="envio-delete"),
    # ******************************* ENVIOS *******************************



    # ******************************* DOWNLAOD *******************************
    path('envio/download/<ids>', download_shipment_labels_file_response,
         name="envio-download-labels"),
    # ******************************* DOWNLAOD *******************************



    # ******************************* BULK *******************************
    path('envio/bulk-add/', bulk_create_envios_view, name="envio-bulk-add"),
    path('envio/bulk-add/<int:pk>/success', success_bulk_create_envios_view,
         name="envio-bulk-add-success"),
    path('envio/bulk-add/<int:pk>/fix',
         handle_bulk_create_envios_view, name="bulk-handle"),
    path('envio/bulk-add/download-excel-to-fix/<int:pk>', print_excel_file,
         name="bulk-download-fix-excel"),
    # ******************************* BULK *******************************
]
