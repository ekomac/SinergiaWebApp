from django.urls import path

from mobile_app.api.views import api_latest_mobile_app_view

app_name = 'mobile-app'

urlpatterns = [
    path('latest', api_latest_mobile_app_view, name="latest"),
]
