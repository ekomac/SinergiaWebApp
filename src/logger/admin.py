from django.contrib import admin
from logger.models import Log
from datetime import datetime, timedelta


def delete_past_60_days(modeladmin, request, queryset):
    d = datetime.today() - timedelta(days=60)
    for log in queryset:
        if log.timestamp < d:
            log.delete()


delete_past_60_days.short_description = 'Eliminar pasados los 60 días'


class LogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'url',)
    search_fields = ('user', 'url',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    actions = (delete_past_60_days,)


admin.site.register(Log, LogAdmin)
