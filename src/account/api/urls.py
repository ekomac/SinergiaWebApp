
from django.urls import path
from account.api.views import (
    ApiCarrierListView,
    api_detail_carrier_view,
    ApiEmployeesWithEnviosListView,

)

app_name = 'account-api'

urlpatterns = [

    path('employees-with-envios/', ApiEmployeesWithEnviosListView.as_view(),
         name="employees-with-envios"),
    path('carriers/', ApiCarrierListView.as_view(),
         name="carriers"),
    path('carrier/<int:pk>/', api_detail_carrier_view,
         name="carrier-detail"),
]
