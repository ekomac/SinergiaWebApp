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
from django.contrib.auth import views as auth_views


from home.views import (
    app_account_view,
    app_view,
    admin_home_screen_view,
    delete_alert_from_session,
    redirect_no_url,
)
from account.views import (
    login_view,
    logout_view,
    forced_reset_password_view,
)

urlpatterns = [
    # BASE
    path('', redirect_no_url),
    path('login/', login_view, name="login"),
    path('reset-password/', forced_reset_password_view,
         name="force_reset_password"),
    path('delete-alert-from-session/<str:id>',
         delete_alert_from_session, name='delete-alert'),
    path('password-change-done/', login_view, name='password_change_done'),
    path('superadmin/', admin.site.urls),

    # ADMIN SITE
    path('admin/', admin_home_screen_view, name='admin-home'),
    path('admin/home', admin_home_screen_view, name='admin-home'),
    path('admin/account/', include('account.urls')),
    path('admin/clients/', include('clients.urls')),
    path('admin/deposits/', include('deposit.urls')),
    path('admin/envios/', include('envios.urls')),
    path('admin/places/', include('places.urls')),
    path('admin/prices/', include('prices.urls')),
    path('admin/summaries/', include('summaries.urls')),
    path('admin/tickets/', include('tickets.urls')),
    path('admin/transactions/', include('transactions.urls')),
    path('admin/change-password/',
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change.html'),
         name='password_change'),
    path('admin/logout/', logout_view, name="logout"),

    # APP
    path('app/', app_view, name="index"),
    path('app/account/', app_account_view, name="baseapp-account"),
    path('app/account/change-password',
         auth_views.PasswordChangeView.as_view(
             template_name='baseapp_account_change_password.html'),
         name="baseapp-account-change-password"),
    path('app/deliver/', include('app_deliver.urls')),
    path('app/deposit/', include('app_deposit.urls')),
    # path('app/tickets/', include('app_tickets.urls')),
    path('app/transfer/', include('app_transfer.urls')),
    path('app/withdraw/', include('app_withdraw.urls')),

    # REST API
    path('api/account/', include('account.api.urls')),
    path('api/deposit/', include('deposit.api.urls', 'deposit_api')),
    path('api/envios/', include('envios.api.urls', 'envios_api')),
    path('api/places/', include('places.api.urls', 'places_api')),
    path('api/tracking/', include('tracking.api.urls', 'tracking_api')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
