from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    EmployeesListView,
    employee_create_view,
    employee_detail_view,
    employee_edit_view,
    employee_delete_view,
)

app_name = 'account'
urlpatterns = [
    path('edit/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change.html'), name="edit"),
    path('', EmployeesListView.as_view(), name="employees-list"),
    path('add/', employee_create_view, name="employees-add"),
    path('<int:pk>/', employee_detail_view, name="employees-detail"),
    path('<int:pk>/edit/', employee_edit_view, name="employees-edit"),
    path('<int:pk>/delete/', employee_delete_view, name="employees-delete"),
    path('<int:pk>/confirm-password-reset/', employee_delete_view,
         name="employees-confirm-password-reset"),
    path('<int:pk>/post/password-reset/', employee_delete_view,
         name="employees-post-password-reset"),
]
