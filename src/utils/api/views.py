from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView


class BaseListAPIView(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = None
    id_in_url_kwarg = None
    query_filter = None
    extra_filters = None

    def get_queryset(self):
        queryset = super(BaseListAPIView, self).get_queryset()
        filters = {}
        if (self.extra_filters is not None and
                isinstance(self.extra_filters, dict)):
            # filters.update(self.extra_filters)
            filters = self.extra_filters
        if self.id_in_url_kwarg is not None and self.query_filter is not None:
            filters[self.query_filter] = self.kwargs.get(self.id_in_url_kwarg)
        # print(filters)
        # print(queryset.filter(**filters))
        print(queryset.filter(**filters).distinct())
        return queryset.filter(**filters).distinct()
