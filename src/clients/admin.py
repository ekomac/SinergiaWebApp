from django.contrib import admin
from clients.models import Client, Discount
from deposit.models import Deposit


class DiscountInline(admin.TabularInline):
    model = Discount


class DepositInline(admin.TabularInline):
    model = Deposit


class ClientAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'created_by', 'name', 'contact_name',
                    'contact_email', 'contact_phone', 'contract',)
    search_fields = ('date_created', 'created_by', 'name', 'contact_name',
                     'contact_email', 'contact_phone', 'contract',)
    inlines = [DiscountInline, DepositInline, ]
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Client, ClientAdmin)
