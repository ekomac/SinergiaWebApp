from django.contrib import admin

from .models import Data


class DataAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_by',
                    'created_at', 'updated_at', 'value')
    search_fields = ('name',
                     'description',
                     'created_by')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Data, DataAdmin)
