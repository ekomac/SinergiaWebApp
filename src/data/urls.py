from django.urls import path

from .views import download_apk

app_name = 'data'
urlpatterns = [
    path('download_apk', download_apk, name="download_apk"),
]
