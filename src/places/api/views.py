from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from places.models import Town
from places.api import TownSerializer


class ApiTownsOfEnviosInDepositListView(ListAPIView):
    queryset = Town.objects.all()
    serializer_class = TownSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    lookup_url_kwarg = "uid"

    def get_queryset(self):
        queryset = super(ApiTownsOfEnviosInDepositListView,
                         self).get_queryset()
        uid = self.kwargs.get(self.lookup_url_kwarg)
        return queryset.filter(destination__receiver__envio__deposit=uid)
