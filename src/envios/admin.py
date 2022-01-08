from django.contrib import admin
from envios.models import (
    BulkLoadEnvios,
    Envio,
)


class EnvioAdmin(admin.ModelAdmin):
    list_display = ('street', 'town',
                    'zipcode', 'client', 'is_flex',
                    'status', 'detail', 'updated_by',
                    'date_created', 'deposit', 'carrier')
    search_fields = ('street',
                     'zipcode', 'is_flex',
                     'status', 'detail', 'date_created',
                     'zipcode', 'deposit', 'carrier')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class BulkLoadEnviosAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'created_by',
                    'load_status', 'client', 'short_csv_result_display',
                    'short_errors_display', 'cells_to_paint',
                    'requires_manual_fix',
                    'hashed_file', 'history')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Envio, EnvioAdmin)
admin.site.register(BulkLoadEnvios, BulkLoadEnviosAdmin)
