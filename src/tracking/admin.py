from django.contrib import admin

from tracking.models import TrackingMovement


class TrackingMovementAdmin(admin.ModelAdmin):
    list_display = ('created_by', 'date_created', 'action', 'result',
                    'comment', 'deposit', 'carrier')
    search_fields = ('created_by', 'action', 'result', 'comment',
                     'deposit', 'carrier')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(TrackingMovement, TrackingMovementAdmin)
