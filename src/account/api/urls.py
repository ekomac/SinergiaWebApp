
from django.urls import path
from account.api.views import (
    ObtainAuthTokenView,
    api_account_properties_view,
    ApiCarrierListView,
    api_detail_carrier_view,
    api_detail_account_view,
    api_check_app_state_view,
    ApiEmployeesWithEnviosListView,
    api_reset_password,

)

app_name = 'account-api'

urlpatterns = [
    path('login/', ObtainAuthTokenView.as_view(), name="login"),
    path('properties/', api_account_properties_view, name="properties"),
    path('employees-with-envios/', ApiEmployeesWithEnviosListView.as_view(),
         name="employees-with-envios"),
    path('carriers/', ApiCarrierListView.as_view(), name="carriers"),
    path('carrier/<int:pk>/', api_detail_carrier_view, name="carrier-detail"),
    path('employee/<int:pk>/', api_detail_account_view,
         name="employee-detail"),
    path('employee/<int:pk>/check-app-state/', api_check_app_state_view,
         name="employee-check-app-state"),
    path('reset-password/', api_reset_password, name="reset-password"),
]
