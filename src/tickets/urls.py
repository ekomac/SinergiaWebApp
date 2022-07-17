from django.urls import path

from .views import (
    list_tickets_view,
    CreateTicketView,
    ticket_detail_view,
    ticket_delete_view,
    ajax_post_message,
    open_ticket_view,
    ajax_close_ticket_view,
    cancel_ticket_view,
    mark_resolved_ticket_view,
    change_priority_ticket_view,
)

app_name = 'tickets'
urlpatterns = [

    path('', list_tickets_view, name="list"),
    path('add/', CreateTicketView.as_view(), name="add"),
    path('<int:pk>/', ticket_detail_view, name="detail"),
    path('<int:pk>/delete/', ticket_delete_view, name="delete"),
    path('<int:ticket_pk>/post-message/user/<int:user_pk>/add',
         ajax_post_message, name="post-message"),
    path('<int:pk>/open/', open_ticket_view, name="open-ticket"),
    path('<int:pk>/close/', ajax_close_ticket_view,
         name="close-ticket"),
    path('<int:pk>/cancel/', cancel_ticket_view, name="cancel-ticket"),
    path('<int:pk>/mark-as-resolve/', mark_resolved_ticket_view,
         name="mark-resolve-ticket"),
    path('<int:pk>/change-priority/<str:priority>/',
         change_priority_ticket_view,
         name="change-priority-ticket"),
]
