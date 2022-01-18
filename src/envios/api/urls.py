
from django.urls import path
from envios.api.views import (
    ApiEnvioListView,

)

app_name = 'envios'

urlpatterns = [
    path('list/', ApiEnvioListView.as_view(), name="list"),
    # path('<slug>/update', api_update_blog_view, name="update"),
    # path('<slug>/delete', api_delete_blog_view, name="delete"),
    # path('create', api_create_blog_view, name="create"),
    # path('list', ApiBlogListView.as_view(), name="list"),
    # path('<slug>/is_author', api_is_author_of_blogpost, name="is_author"),
]
