from django.urls import path

from .views import (
    ClientSummaryListView,
    EmployeeSummaryListView,
    ajax_get_employee_summaries_total_cost,
    client_summary_create_view,
    client_summary_detail_view,
    employee_summary_create_view,
    employee_summary_detail_view,
    print_csv_client_summary,
    print_xls_client_summary,
    print_pdf_client_summary,
    print_csv_employee_summary,
    print_xls_employee_summary,
    print_pdf_employee_summary,
    ajax_get_client_summary_total_cost,
    ajax_get_client_summaries_total_cost,
    ajax_get_employee_summary_total_cost,
)

app_name = 'summaries'
urlpatterns = [
    path(
        'clients/', ClientSummaryListView.as_view(),
        name="client-list"),
    path(
        'clients/add/', client_summary_create_view, name="client-add"),
    path(
        'clients/<int:pk>/', client_summary_detail_view,
        name="client-detail"),
    path(
        'clients/<int:pk>/print-csv/', print_csv_client_summary,
        name="client-print-csv"),
    path(
        'clients/<int:pk>/print-xls/', print_xls_client_summary,
        name="client-print-excel"),
    path(
        'clients/<int:pk>/print-pdf/', print_pdf_client_summary,
        name="client-print-pdf"),
    path(
        'employees/', EmployeeSummaryListView.as_view(),
        name="employee-list"),
    path(
        'employees/add/', employee_summary_create_view, name="employee-add"),
    path(
        'employees/<int:pk>/', employee_summary_detail_view,
        name="employee-detail"),
    path(
        'employees/<int:pk>/print-csv/', print_csv_employee_summary,
        name="employee-print-csv"),
    path(
        'employees/<int:pk>/print-xls/', print_xls_employee_summary,
        name="employee-print-excel"),
    path(
        'employees/<int:pk>/print-pdf/', print_pdf_employee_summary,
        name="employee-print-pdf"),
    path(
        'employees/<int:pk>/total-cost/', ajax_get_employee_summary_total_cost,
        name="employee-summary-total-cost"),
    path(
        'employees/total-cost/<str:pks>',
        ajax_get_employee_summaries_total_cost,
        name="employee-summaries-total-cost"),
    path(
        'clients/<int:pk>/total-cost/', ajax_get_client_summary_total_cost,
        name="client-summary-total-cost"),
    path(
        'clients/total-cost/<str:pks>', ajax_get_client_summaries_total_cost,
        name="client-summaries-total-cost"),


]
