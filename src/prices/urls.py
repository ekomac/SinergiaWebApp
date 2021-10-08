from django.urls import path

from .views import (
    # Listing
    dcodes_view,
    fcodes_view,

    # Creating
    AddDCodeView,
    AddFCodeView,

    # Detailing
    DCodeDetailView,
    FCodeDetailView,

    # Updating

    # Deleting
    confirm_delete_dcode,
    confirm_delete_fcode,
)

app_name = 'prices'
urlpatterns = [
    # Listing
    path('delivery/', dcodes_view, name="dlist"),
    path('flex/', fcodes_view, name="flist"),

    # Creating
    path('delivery/add/', AddDCodeView.as_view(), name="dcode-add"),
    path('flex/add/', AddFCodeView.as_view(), name="fcode-add"),

    # Detailing
    path('delivery/<int:pk>/', DCodeDetailView.as_view(), name="ddetail"),
    path('flex/<int:pk>/', FCodeDetailView.as_view(), name="fdetail"),

    # Updating
    #
    #

    # Deleting
    path('delivery/delete/<dcodesids>/',
         confirm_delete_dcode, name="delete-dcodes"),
    path('flex/delete/<fcodeids>/',
         confirm_delete_fcode, name='delete-fcodes'),

]
