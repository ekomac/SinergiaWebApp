from django.urls import path

from .views import (
    TransactionsListView,
    transaction_create_view,
    transaction_edit_view,
    transaction_delete_view,
    print_csv,
    print_xlsx,
    print_pdf,
)

app_name = 'transactions'
urlpatterns = [
    path('', TransactionsListView.as_view(), name="list"),
    path('add/', transaction_create_view, name="add"),
    path('<int:pk>/edit/', transaction_edit_view, name="edit"),
    path('<int:pk>/delete/', transaction_delete_view, name="delete"),
    path('export/csv/', print_csv, name="print-csv"),
    path('export/xlsx/', print_xlsx, name="print-xlsx"),
    path('export/pdf/', print_pdf, name="print-pdf"),
]
