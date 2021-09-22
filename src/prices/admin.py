from django.contrib import admin
from prices.models import DeliveryCode, FlexCode


class DeliveryCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'price')
    search_fields = ('code',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class FlexCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'price')
    search_fields = ('code',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(DeliveryCode, DeliveryCodeAdmin)
admin.site.register(FlexCode, FlexCodeAdmin)
