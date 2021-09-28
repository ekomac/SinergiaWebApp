from django.urls import path
from .views import edit_account_view

app_name = 'account'
urlpatterns = [
    path('edit/', edit_account_view, name="edit"),
]
