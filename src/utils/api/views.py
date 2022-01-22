from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView


class BaseListAPIView(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    id_in_url_kwarg = None
    query_filter = None

    def get_queryset(self):
        queryset = super(BaseListAPIView, self).get_queryset()
        if self.id_in_url_kwarg is None or self.query_filter is None:
            return queryset
        uid = self.kwargs.get(self.id_in_url_kwarg)
        return queryset.filter(**{self.query_filter: uid}).distinct()
