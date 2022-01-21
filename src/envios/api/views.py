# REST FRAMEWORK
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter


# PROJECT
from envios.api.serializers import EnvioSerializer
from envios.models import Envio


class ApiEnvioListView(ListAPIView):
    queryset = Envio.objects.all()
    serializer_class = EnvioSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('first_name', 'last_name', 'username', 'email')
    # Explicitly specify which fields the API may be ordered against
    ordering_fields = ('date_created',)
    ordering = ('date_created',)

    lookup_url_kwargs = (
        ('deposit', 'deposit__id',),
        ('status', 'status__in',),
    )

    def get_queryset(self):
        queryset = super(ApiEnvioListView, self).get_queryset()
        filters = {}
        deposit = self.request.query_params.get('deposit', None)
        if deposit is not None:
            filters['deposit__id'] = deposit
            queryset = queryset.filter(deposit__id=deposit)
        status = self.request.query_params.get('status', None)
        if status is not None:
            if "-" in status:
                status = status.split('-')
            filters['status__in'] = [status] if isinstance(
                status, str) else status
        return queryset.filter(**filters)

