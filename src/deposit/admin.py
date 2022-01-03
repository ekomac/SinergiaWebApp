from django.contrib import admin
from deposit.models import Deposit


class DepositAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'created_by', 'is_active',
                    'client', 'name', 'address', 'zip_code', 'town',
                    'phone', 'email')
    search_fields = ('created_by', 'is_active',
                     'client', 'name', 'address', 'zip_code', 'town',
                     'phone', 'email')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Deposit, DepositAdmin)
