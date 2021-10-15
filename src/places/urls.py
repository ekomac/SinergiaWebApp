from django.urls import path

from places.views import (

    # ******** TOWN ********
    towns_view,
    TownDetailView,
    TownUpdateView,
    # ******** TOWN ********


    # ******** ZONE ********
    zones_view,
    add_zone_view,
    ZoneDetailView,
    edit_zone_view,
    zone_delete,
    # ******** ZONE ********

)

app_name = 'places'
urlpatterns = [

    # **************************** TOWN ****************************
    path('town', towns_view, name="town-list"),
    path('town/<int:pk>', TownDetailView.as_view(), name="town-detail"),
    path('town/<int:pk>/edit', TownUpdateView.as_view(), name="town-edit"),
    # **************************** TOWN ****************************


    # **************************** ZONE ****************************
    path('zone/', zones_view, name="zone-list"),
    path('zone/add', add_zone_view, name="zone-add"),
    path('zone/<int:pk>', ZoneDetailView.as_view(), name="zone-detail"),
    path('zone/<int:pk>/edit/', edit_zone_view, name="zone-edit"),
    path('zone/<zoneids>/delete', zone_delete, name="zone-delete"),
    # **************************** ZONE ****************************
]
