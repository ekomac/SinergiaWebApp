from django.contrib import admin

from tickets.models import Attachment, Ticket, TicketMessage


class AttachmentInline(admin.TabularInline):
    model = Attachment


class TicketAdmin(admin.ModelAdmin):
    list_display = ('priority', 'subject', 'msg', 'status', 'closed_reason',)
    search_fields = ('priority', 'subject', 'msg', 'status', 'closed_reason',)
    inlines = [AttachmentInline, ]
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'created_by', 'msg', 'ticket',)
    search_fields = ('msg',)


admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketMessage, TicketMessageAdmin)
