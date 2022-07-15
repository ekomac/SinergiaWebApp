from django.contrib import admin
from django.conf import settings
from envios.models import (
    BulkLoadEnvios,
    Envio,
)
from envios.debug_actions import actions as debug_actions


class EnvioAdmin(admin.ModelAdmin):
    list_display = ('street', 'town',
                    'zipcode', 'client', 'is_flex',
                    'status', 'detail', 'updated_by',
                    'date_created', 'deposit', 'carrier')
    search_fields = ('street',
                     'zipcode', 'is_flex',
                     'status', 'detail', 'date_created',
                     'zipcode', 'deposit', 'carrier')
    actions = debug_actions if settings.DEBUG else []

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class BulkLoadEnviosAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'created_by',
                    'load_status', 'client', 'short_csv_result_display',
                    'short_errors_display', 'cells_to_paint',
                    'requires_manual_fix',
                    'hashed_file', 'original_file')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Envio, EnvioAdmin)
admin.site.register(BulkLoadEnvios, BulkLoadEnviosAdmin)
