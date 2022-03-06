from django.urls import path
from mobile.deliver.views import (
    scan_view,
    select_result_view,
    confirm_result_view,
    confirm_other_view
)


app_name = 'mobile-deliver'

urlpatterns = [

    # SELECT ENVIO FROM SCANNER
    path('', scan_view, name="scan"),

    # SELECT RESULT
    path('result',
         select_result_view, name="select-result"),

    # CONFIRM SELECTED FROM SCANNER
    path('result/confirm',
         confirm_result_view, name="confirm-result"),

    path('result/confirm/other',
         confirm_other_view, name="confirm-other"),
]
