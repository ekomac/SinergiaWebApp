from django.contrib import admin

from changes.models import Change


class ChangesAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'author', 'name', 'description')


admin.site.register(Change, ChangesAdmin)
