from django.urls import path

from places.views import (
    towns_view,
    TownDetailView,
    TownUpdateView,
)

app_name = 'places'
urlpatterns = [

    # **************************** TOWN ****************************
    path('', towns_view, name="town-list"),
    path('<int:pk>', TownDetailView.as_view(),
         name="town-detail"),
    path('<int:pk>/edit', TownUpdateView.as_view(),
         name="town-edit"),
    # **************************** TOWN ****************************
]
