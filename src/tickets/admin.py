from django.contrib import admin

from tickets.models import Attachment, EmailLog, Ticket, TicketMessage


class AttachmentInline(admin.TabularInline):
    model = Attachment


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'ticket', 'file',)
    search_fields = ('ticket',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class TicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'priority', 'msg', 'status', 'closed_reason',)
    search_fields = ('priority', 'subject', 'msg', 'status', 'closed_reason',)
    inlines = [AttachmentInline, ]
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'created_by', 'msg',
                    'ticket', 'is_priority_update',)
    ordering = ('-date_created',)
    search_fields = ('msg',)


class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'msg', 'ticket',
                    'ticket_msg', 'function_name',)
    ordering = ('-date_created',)
    search_fields = ('msg',)


admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketMessage, TicketMessageAdmin)
admin.site.register(EmailLog, EmailLogAdmin)
