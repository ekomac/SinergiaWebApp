from django.contrib import admin

from tickets.models import Ticket


class TicketAdmin(admin.ModelAdmin):
    list_display = ('priority', 'subject', 'msg', 'status', 'closed_reason',)
    search_fields = ('priority', 'subject', 'msg', 'status', 'closed_reason',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Ticket, TicketAdmin)
