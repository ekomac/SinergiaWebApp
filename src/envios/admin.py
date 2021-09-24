from django.contrib import admin
from envios.models import Deposit, Envio, Bolson, TrackingMovement


class EnvioAdmin(admin.ModelAdmin):
    list_display = ('recipient_town', 'recipient_address',
                    'recipient_zipcode', 'client', 'is_flex',
                    'status', 'detail', 'created_by', 'date_created',)
    search_fields = ('recipient_town', 'recipient_address',
                     'recipient_zipcode', 'client', 'is_flex',
                     'status', 'detail', 'date_created',
                     'created_by', 'recipient_zipcode',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class BolsonAdmin(admin.ModelAdmin):
    list_display = ('carrier', 'datetime_created',)
    search_fields = ('carrier', 'datetime_created',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class DepositAdmin(admin.ModelAdmin):
    list_display = ('name', 'town', 'is_ours', 'client',)
    search_fields = ('name', 'town', 'is_ours', 'client',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class TrackingMovementAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_time', 'action', 'result',
                    'comment', 'deposit',)
    search_fields = ('user', 'action', 'result', 'comment',
                     'deposit',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Envio, EnvioAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(Bolson, BolsonAdmin)
admin.site.register(TrackingMovement, TrackingMovementAdmin)
