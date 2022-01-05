from django.contrib import admin

from tickets.models import Attachment, Ticket


class FileInline(admin.TabularInline):
    model = Attachment


class TicketAdmin(admin.ModelAdmin):
    list_display = ('priority', 'subject', 'msg', 'status', 'closed_reason',)
    search_fields = ('priority', 'subject', 'msg', 'status', 'closed_reason',)
    inlines = [FileInline, ]
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Ticket, TicketAdmin)
