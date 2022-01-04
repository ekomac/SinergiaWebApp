from django.urls import path

from .views import list_tickets_view, ticket_detail_view, ticket_delete_view

app_name = 'tickets'
urlpatterns = [

    # ******************************* ENVIOS *******************************
    path('', list_tickets_view, name="list"),
    path('<int:pk>/', ticket_detail_view, name="detail"),
    path('<int:pk>/delete/', ticket_delete_view, name="delete"),
]
