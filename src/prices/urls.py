from django.urls import path

from .views import (

    # ******** MENSAJERIA ********
    delivery_codes_view,
    DeliveryCodeAddView,
    DeliveryCodeDetailView,
    DeliveryCodeUpdateView,
    delivery_code_delete,
    # ******** MENSAJERIA ********

    # ********* FLEX *********
    flex_codes_view,
    FlexCodeAddView,
    FlexCodeDetailView,
    FlexCodeUpdateView,
    flex_code_delete,
    # ********* FLEX *********
)

app_name = 'prices'
urlpatterns = [

    # **************************** MENSAJERIA ****************************
    path('delivery', delivery_codes_view, name="dcode-list"),
    path('delivery/add', DeliveryCodeAddView.as_view(), name="dcode-add"),
    path('delivery/<int:pk>/', DeliveryCodeDetailView.as_view(),
         name="dcode-detail"),
    path('delivery/<int:pk>/edit', DeliveryCodeUpdateView.as_view(),
         name="dcode-edit"),
    path('delivery/delete/<dcodeids>', delivery_code_delete,
         name="dcode-delete"),
    # **************************** MENSAJERIA ****************************


    # ****************************** FLEX ******************************
    path('flex', flex_codes_view, name="fcode-list"),
    path('flex/add', FlexCodeAddView.as_view(), name="fcode-add"),
    path('flex/<int:pk>/', FlexCodeDetailView.as_view(), name="fcode-detail"),
    path('flex/<int:pk>/edit', FlexCodeUpdateView.as_view(),
         name="fcode-edit"),
    path('flex/delete/<fcodeids>', flex_code_delete,
         name='fcode-delete'),
    # ****************************** FLEX ******************************
]
