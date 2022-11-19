from django.urls import path

from places.views import (
    TownListView,
    print_towns_and_prices_excel_file
)

app_name = 'places'
urlpatterns = [
    path('town', TownListView.as_view(), name="town-list"),
    path('download_list', print_towns_and_prices_excel_file,
         name="download-towns-list")
]
