from django.contrib import admin
from mobile_app.models import MobileApp


class MobileAppAdmin(admin.ModelAdmin):
    list_display = (
        'latest_version',
        'url',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'latest_version',
        'url',
    )
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(MobileApp, MobileAppAdmin)
