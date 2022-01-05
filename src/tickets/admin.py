from django.contrib import admin

from tickets.models import Attachment, Ticket


class AttachmentInline(admin.TabularInline):
    model = Attachment


class TicketAdmin(admin.ModelAdmin):
    list_display = ('priority', 'subject', 'msg', 'status', 'closed_reason',)
    search_fields = ('priority', 'subject', 'msg', 'status', 'closed_reason',)
    inlines = [AttachmentInline, ]
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Ticket, TicketAdmin)
