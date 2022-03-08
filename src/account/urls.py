from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    EmployeesListView,
    create_user_view,
    update_user_view,
    employee_detail_view,
    employee_delete_view,
    ajax_password_reset,
    enable_account_and_return_to_detail_view,
    disable_account_and_return_to_detail_view,
)

app_name = 'account'
urlpatterns = [
    path('edit/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change.html'), name="edit"),
    path('', EmployeesListView.as_view(), name="employees-list"),
    path('add/', create_user_view, name="employees-add"),
    path('<int:pk>/', employee_detail_view, name="employees-detail"),
    path('<int:pk>/edit/', update_user_view, name="account-edit"),
    path('<int:pk>/enable/',
         enable_account_and_return_to_detail_view, name="enable-account"),
    path('<int:pk>/disable/',
         disable_account_and_return_to_detail_view, name="disable-account"),
    path('<int:pk>/delete/', employee_delete_view, name="employees-delete"),
    path('<int:pk>/confirm-password-reset/', employee_delete_view,
         name="employees-confirm-password-reset"),
    path('<int:pk>/post/password-reset/', ajax_password_reset,
         name="post-password-reset"),
]
