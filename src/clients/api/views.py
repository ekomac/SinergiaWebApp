from clients.models import Client
from clients.api.serializers import ClientSerializer
from envios.models import Envio
from utils.api.views import BaseListAPIView


class ApiClientsAtDepositListView(BaseListAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    id_in_url_kwarg = 'deposit_id'
    query_filter = 'envio__deposit__id'
    extra_filters = {
        'envio__status__in': [
            Envio.STATUS_STILL, Envio.STATUS_NEW],
    }
