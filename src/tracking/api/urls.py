
from django.urls import path
from tracking.api.views import (
    api_withdraw_all_view,
    api_withdraw_by_ids_view,
    api_withdraw_by_filter_view
)

app_name = 'tracking'

urlpatterns = [
    path('withdraw/all/', api_withdraw_all_view, name="api-withdraw-all"),
    path('withdraw/ids/', api_withdraw_by_ids_view, name="api-withdraw-ids"),
    path('withdraw/filtered/', api_withdraw_by_filter_view,
         name="api-withdraw-by-filter"),
    # path('withdraw/one', post_withdraw_view, name="post-withdraw-one"),
    # path('withdraw/by_filter', post_withdraw_view,
    #      name="post-withdraw-filtered"),
    # path('<slug>/update', api_update_blog_view, name="update"),
    # path('<slug>/delete', api_delete_blog_view, name="delete"),
    # path('create', api_create_blog_view, name="create"),
    # path('list', ApiBlogListView.as_view(), name="list"),
    # path('<slug>/is_author', api_is_author_of_blogpost, name="is_author"),
]
