from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.models import Token
from account.models import Account


def refresh_token(modeladmin, request, queryset):
    for account in queryset:
        token: Token = Token.objects.filter(user=account)
        new_key = token[0].generate_key()
        token.update(key=new_key)


refresh_token.short_description = 'Refrescar token'


def force_password_reset(modeladmin, request, queryset):
    for account in queryset:
        token: Token = Token.objects.filter(user=account)
        new_key = token[0].generate_key()
        token.update(key=new_key)
        account.set_password(settings.DEFAULT_RESET_PASSWORD)
        account.has_to_reset_password = True
        account.save()


force_password_reset.short_description = 'Forzar cambio de contraseña'


class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name',
                    'last_name', 'is_admin', 'is_staff',
                    'last_login', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name',)
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    actions = [refresh_token, force_password_reset]


admin.site.register(Account, AccountAdmin)
