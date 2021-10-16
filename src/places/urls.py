from django.urls import path

from places.views import (

    # ******** PARTIDO ********
    partidos_view,
    PartidoDetailView,
    edit_partido_view,
    bulk_edit_partidos_view,
    # ******** PARTIDO ********


    # ******** TOWN ********
    towns_view,
    TownDetailView,
    TownUpdateView,
    bulk_edit_town_delivery_view,
    bulk_edit_town_flex_view,
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

    # ****************************** PARTIDO ******************************
    path('partido', partidos_view, name="partido-list"),
    path('partido/<int:pk>', PartidoDetailView.as_view(),
         name="partido-detail"),
    path('partido/<int:pk>/edit', edit_partido_view, name="partido-edit"),
    path('partido/<partidosids>/edit',
         bulk_edit_partidos_view, name="partido-bulk-edit"),
    # ****************************** PARTIDO ******************************


    # **************************** TOWN ****************************
    path('town', towns_view, name="town-list"),
    path('town/<int:pk>', TownDetailView.as_view(), name="town-detail"),
    path('town/<int:pk>/edit', TownUpdateView.as_view(), name="town-edit"),
    path('town/<townsids>/bulk_edit',
         bulk_edit_partidos_view, name="partido-bulk-edit"),
    path('town/<townsids>/bulk_edit',
         bulk_edit_partidos_view, name="partido-bulk-edit"),
    # **************************** TOWN ****************************


    # **************************** ZONE ****************************
    path('zone/', zones_view, name="zone-list"),
    path('zone/add', add_zone_view, name="zone-add"),
    path('zone/<int:pk>', ZoneDetailView.as_view(), name="zone-detail"),
    path('zone/<int:pk>/edit/', edit_zone_view, name="zone-edit"),
    path('zone/<zoneids>/delete', zone_delete, name="zone-delete"),
    # **************************** ZONE ****************************
]
