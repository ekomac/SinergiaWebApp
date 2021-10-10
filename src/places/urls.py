from django.urls import path

from places.views import (
    towns_view_2,
    TownAddView,
    TownDetailView,
    TownUpdateView,
    town_delete,
)

app_name = 'places'
urlpatterns = [

    # **************************** TOWN ****************************
    path('', towns_view_2, name="town-list"),
    path('add', TownAddView.as_view(), name="town-add"),
    path('<int:pk>', TownDetailView.as_view(),
         name="town-detail"),
    path('<int:pk>/edit', TownUpdateView.as_view(),
         name="town-edit"),
    path('delete/<townids>', town_delete,
         name="town-delete"),
    # **************************** TOWN ****************************
]
