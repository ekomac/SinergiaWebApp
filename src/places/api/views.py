from envios.models import Envio
from places.models import Partido, Town, Zone
from places.api.serializers import (
    PartidoSerializer, TownSerializer, ZoneSerializer)
from utils.api.views import BaseListAPIView


class ApiTownsAtDepositListView(BaseListAPIView):
    queryset = Town.objects.all()
    serializer_class = TownSerializer
    id_in_url_kwarg = 'deposit_id'
    query_filter = 'destination__receiver__envio__deposit__id'
    extra_filters = {
        'destination__receiver__envio__status__in': [
            Envio.STATUS_STILL, Envio.STATUS_NEW],
    }


class ApiPartidosAtDepositListView(BaseListAPIView):
    queryset = Partido.objects.all()
    serializer_class = PartidoSerializer
    id_in_url_kwarg = 'deposit_id'
    query_filter = 'town__destination__receiver__envio__deposit__id'
    extra_filters = {
        'town__destination__receiver__envio__status__in': [
            Envio.STATUS_STILL, Envio.STATUS_NEW],
    }


class ApiZonesAtDepositListView(BaseListAPIView):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    id_in_url_kwarg = 'deposit_id'
    query_filter = 'partido__town__destination__receiver__envio__deposit__id'
    extra_filters = {
        'partido__town__destination__receiver__envio__status__in': [
            Envio.STATUS_STILL, Envio.STATUS_NEW],
    }


class ApiTownsAtCarrierListView(BaseListAPIView):
    queryset = Town.objects.all()
    serializer_class = TownSerializer
    id_in_url_kwarg = 'carrier_id'
    query_filter = 'destination__receiver__envio__carrier__id'
    extra_filters = {
        'destination__receiver__envio__status': Envio.STATUS_MOVING,
    }


class ApiPartidosAtCarrierListView(BaseListAPIView):
    queryset = Partido.objects.all()
    serializer_class = PartidoSerializer
    id_in_url_kwarg = 'carrier_id'
    query_filter = 'town__destination__receiver__envio__carrier__id'
    extra_filters = {
        'town__destination__receiver__envio__status': Envio.STATUS_MOVING,
    }


class ApiZonesAtCarrierListView(BaseListAPIView):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    id_in_url_kwarg = 'carrier_id'
    query_filter = 'partido__town__destination__receiver__envio__carrier__id'
    part_one = 'partido__town__destination__'
    part_two = 'receiver__envio__status'
    extra_filters = {
        part_one + part_two: Envio.STATUS_MOVING,
    }

# class ApiTownsOfEnviosInDepositListView(ListAPIView):
#     queryset = Town.objects.all()
#     serializer_class = TownSerializer
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#     pagination_class = PageNumberPagination
#     lookup_url_kwarg = "deposit_id"

#     def get_queryset(self):
#         queryset = super(ApiTownsOfEnviosInDepositListView,
#                          self).get_queryset()
#         uid = self.kwargs.get(self.lookup_url_kwarg)
#         return queryset.filter(destination__receiver__envio__deposit=uid)
