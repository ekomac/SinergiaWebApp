from django.urls import path

from .views import (
    summary_list_view,
    summary_create_view,
    summary_detail_view,
    print_csv_summary,
    print_xls_summary,
    print_pdf_summary,
)

app_name = 'summaries'
urlpatterns = [
    path('', summary_list_view, name="list"),
    path('add/', summary_create_view, name="add"),
    path('<int:pk>/', summary_detail_view, name="detail"),
    path('<int:pk>/print-csv/', print_csv_summary, name="print-csv"),
    path('<int:pk>/print-xls/', print_xls_summary, name="print-excel"),
    path('<int:pk>/print-pdf/', print_pdf_summary, name="print-pdf"),
]
