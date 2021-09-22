from django.contrib import admin
from places.models import Partido, Town, Zone


class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'asigned_to')
    search_fields = ('name', 'asigned_to')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class PartidoAdmin(admin.ModelAdmin):
    list_display = ('name', 'province', 'amba_zone')
    search_fields = ('name', 'province', 'amba_zone')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class TownAdmin(admin.ModelAdmin):
    list_display = ('name', 'partido', 'delivery_code', 'flex_code')
    search_fields = ('name', 'partido', 'delivery_code', 'flex_code')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Zone, ZoneAdmin)
admin.site.register(Partido, PartidoAdmin)
admin.site.register(Town, TownAdmin)
