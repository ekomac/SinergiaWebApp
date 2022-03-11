from django.urls import path

from places.views import TownListView
from prices.views import (
    DeliveryCodeListView,
    FlexCodeListView,
    calcular_cotizacion_view,
    cotizador_view)

from .views import (
    CustomPasswordChangeView,
    IndexEnvioListView,
    EnvioDetailView,
    EnvioCreate,
    bulk_create_envios_view,
    handle_bulk_create_envios_view,
    post_selected_ids,
    download_single_shipment_label_file_response,
    download_shipment_labels_file_response,
    success_bulk_create_envios_view,
    print_excel_file,
    edit_envio_view,
    cancel_envio_view,
)

app_name = 'clients_only'
urlpatterns = [


    # ******************************* ENVIOS *******************************
    path('', IndexEnvioListView.as_view(), name="index"),
    path('add/', EnvioCreate.as_view(), name="envio-add"),
    path('<int:pk>/', EnvioDetailView.as_view(), name="envio-detail"),
    path('<int:pk>/edit/', edit_envio_view, name="envio-edit"),
    path('<int:pk>/cancel/', cancel_envio_view, name="envio-cancel"),
    # ******************************* ENVIOS *******************************


    # ******************************* DOWNLAOD *******************************
    path('post_ids/', post_selected_ids, name="post-selected-ids"),
    path('download/<int:pk>/', download_single_shipment_label_file_response,
         name="single-envio-download-label"),
    path('download/', download_shipment_labels_file_response,
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

    path('towns/', TownListView.as_view(), name="town-list"),

    path('cotizador/', cotizador_view, name='cotizador'),
    path('cotizador/calculate/', calcular_cotizacion_view,
         name='calcular-cotizacion'),
    path('delivery/', DeliveryCodeListView.as_view(), name="dcode-list"),
    path('flex/', FlexCodeListView.as_view(), name='fcode-list'),
    path('account/edit-password/', CustomPasswordChangeView.as_view(
        template_name='registration/password_change.html'),
        name='edit-password'),
]
