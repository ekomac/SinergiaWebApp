from django.urls import path

from .views import (
    list_tickets_view,
    CreateTicketView,
    ticket_detail_view,
    ticket_delete_view
)

app_name = 'tickets'
urlpatterns = [

    # ******************************* ENVIOS *******************************
    path('', list_tickets_view, name="list"),
    path('add/', CreateTicketView.as_view(), name="add"),
    path('<int:pk>/', ticket_detail_view, name="detail"),
    path('<int:pk>/delete/', ticket_delete_view, name="delete"),
]
