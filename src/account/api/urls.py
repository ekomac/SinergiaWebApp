
from django.urls import path
from account.api.views import (
    ApiCarrierListView,
    api_detail_carrier_view,

)

app_name = 'account'

urlpatterns = [
    path('carrier/', ApiCarrierListView.as_view(), name="carrier-list"),
    path('carrier/<int:pk>/', api_detail_carrier_view, name="carrier-detail"),
]
