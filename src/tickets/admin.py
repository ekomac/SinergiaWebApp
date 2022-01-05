from django.contrib import admin

from tickets.models import File, Ticket


class FileInline(admin.TabularInline):
    model = File


class TicketAdmin(admin.ModelAdmin):
    list_display = ('priority', 'subject', 'msg', 'status', 'closed_reason',)
    search_fields = ('priority', 'subject', 'msg', 'status', 'closed_reason',)
    inlines = [FileInline, ]
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Ticket, TicketAdmin)
