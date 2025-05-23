from django.urls import path

from .views import (
    ClientListView,
    create_client_view,
    edit_client_view,
    activate_client_view,
    deactivate_client_view,
    client_detail_view,
    # client_delete_view,
    add_discount_view,
    edit_discount_view,
    delete_discount_view,
)

app_name = 'clients'
urlpatterns = [
    path('', ClientListView.as_view(), name="list"),
    path('add/', create_client_view, name="add"),
    path('<int:pk>/', client_detail_view, name="detail"),
    path('<int:pk>/edit/', edit_client_view, name="edit"),
    path('<int:pk>/activate/', activate_client_view, name="activate"),
    path('<int:pk>/deactivate/', deactivate_client_view, name="deactivate"),
    # path('<int:pk>/delete/', client_delete_view, name="delete"),
    path('<int:pk>/add-discount/', add_discount_view, name="add-discount"),
    path('<int:client_pk>/discount/<int:discount_pk>/edit',
         edit_discount_view, name="edit-discount"),
    path('<int:client_pk>/discount/<int:discount_pk>/delete',
         delete_discount_view, name="delete-discount"),
]
