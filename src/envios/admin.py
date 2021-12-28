from django.contrib import admin
from envios.models import (
    BulkLoadEnvios,
    Envio,
    Bolson,
    TrackingMovement
)


class EnvioAdmin(admin.ModelAdmin):
    list_display = ('street', 'town',
                    'zipcode', 'client', 'is_flex',
                    'status', 'detail', 'created_by',
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


class BolsonAdmin(admin.ModelAdmin):
    list_display = ('carrier', 'datetime_created',)
    search_fields = ('carrier', 'datetime_created',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class DepositOldAdmin(admin.ModelAdmin):
    list_display = ('name', 'town', 'central', 'client',)
    search_fields = ('name', 'town', 'central', 'client',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class TrackingMovementAdmin(admin.ModelAdmin):
    list_display = ('created_by', 'date_created', 'action', 'result',
                    'comment', 'deposit', 'carrier')
    search_fields = ('created_by', 'action', 'result', 'comment',
                     'deposit', 'carrier')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Envio, EnvioAdmin)
admin.site.register(BulkLoadEnvios, BulkLoadEnviosAdmin)
admin.site.register(Bolson, BolsonAdmin)
admin.site.register(TrackingMovement, TrackingMovementAdmin)
