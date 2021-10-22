from django.contrib import admin
from places.models import Partido, ZipCode, Town, Zone


class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'asigned_to')
    search_fields = ('name', 'asigned_to__first_name', 'asigned_to__last_name')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class PartidoAdmin(admin.ModelAdmin):
    list_display = ('name', 'province', 'zone')
    search_fields = ('name', 'province', 'zone__name')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class TownAdmin(admin.ModelAdmin):
    list_display = ('name', 'partido', 'delivery_code', 'flex_code')
    search_fields = ('name',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class ZipCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'created_by', 'date_created')
    search_fields = ('code',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Zone, ZoneAdmin)
admin.site.register(Partido, PartidoAdmin)
admin.site.register(Town, TownAdmin)
admin.site.register(ZipCode, ZipCodeAdmin)
