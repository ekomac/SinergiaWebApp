from django.urls import path, include


app_name = 'mobile'

urlpatterns = [
    path('deliver/', include('mobile.deliver.urls', 'mobile-deliver')),
    path('deposit/', include('mobile.deposit.urls', 'mobile-deposit')),
    path('transfer/', include('mobile.transfer.urls', 'mobile-transfer')),
    path('withdraw/', include('mobile.withdraw.urls', 'mobile-withdraw')),
]
