"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from home.views import (
    app_view,
    admin_home_screen_view,
    prueba_view,
    delete_alert_from_session,
    redirect_no_url,
)
from account.views import (
    login_view,
    logout_view,
)

urlpatterns = [
    path('admin/home', admin_home_screen_view, name='admin-home'),
    path('admin/account/', include('account.urls')),
    path('superadmin/', admin.site.urls),
    path('login/', login_view, name="login"),
    path('admin/logout/', logout_view, name="logout"),
    path('admin/envios/', include('envios.urls')),
    path('admin/prueba/', prueba_view, name='prueba'),
    path('admin/prices/', include('prices.urls')),
    path('admin/places/', include('places.urls')),
    path('app/', app_view, name="index"),
    path('app/withdraw/', include('app_withdraw.urls')),
    path('app/deposit/', include('app_deposit.urls')),
    path('app/transfer/', include('app_transfer.urls')),
    # path('app/deliver/', include('app_deliver.urls')),
    path('', redirect_no_url),
    path('delete-alert-from-session/<str:id>',
         delete_alert_from_session, name='delet-alert'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
