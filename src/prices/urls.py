from django.urls import path

from .views import (
    dcodes_view,
    fcodes_view,
    AddDCodeView,
    AddFCodeView,
    DCodeDetailView,
    FCodeDetailView
)

app_name = 'prices'
urlpatterns = [
    path('delivery/', dcodes_view, name="dlist"),
    path('delivery/add/', AddDCodeView.as_view(), name="d-add"),
    path('delivery/<int:pk>/', DCodeDetailView.as_view(), name="ddetail"),
    path('flex/', fcodes_view, name="flist"),
    path('flex/add/', AddFCodeView.as_view(), name="f-add"),
    path('flex/<int:pk>/', FCodeDetailView.as_view(), name="fdetail"),
    # path('<int:pk>/', , name="detail"),
    # path('add/', , name="create"),
    # path('edit/', , name="edit"),
    # path('delete/', , name="delete"),
]
