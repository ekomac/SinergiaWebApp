from django.urls import path

from .views import (
    list_tickets_view,
    CreateTicketView,
    ticket_detail_view,
    ticket_delete_view,
    ajax_post_message,
    open_ticket_view,
    ajax_close_ticket_view,
)

app_name = 'tickets'
urlpatterns = [

    # ******************************* ENVIOS *******************************
    path('', list_tickets_view, name="list"),
    path('add/', CreateTicketView.as_view(), name="add"),
    path('<int:pk>/', ticket_detail_view, name="detail"),
    path('<int:pk>/delete/', ticket_delete_view, name="delete"),
    path('post-message/ticket/<int:ticket_pk>/user/<int:user_pk>/add',
         ajax_post_message, name="post-message"),
    path('open-ticket/<int:pk>/', open_ticket_view, name="open-ticket"),
    path('close-ticket/<int:pk>/', ajax_close_ticket_view,
         name="close-ticket"),
]
