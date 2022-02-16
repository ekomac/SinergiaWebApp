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


class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name',
                    'last_name', 'is_admin', 'is_staff',
                    'last_login', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name',)
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    actions = [refresh_token]


admin.site.register(Account, AccountAdmin)
