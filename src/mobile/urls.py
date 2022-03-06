from django.urls import path
from home.views import (
    mobile_account_view,
    mobile_based_tracking_actions_view,
)


app_name = 'mobile'

urlpatterns = [
    path('', mobile_based_tracking_actions_view, name="index"),
    path('account/', mobile_account_view, name="account"),
]
