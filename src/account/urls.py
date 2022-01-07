from django.urls import path
from django.contrib.auth import views as auth_views
# from .views import edit_account_view

app_name = 'account'
urlpatterns = [
    path('edit/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change.html'), name="edit"),
]
