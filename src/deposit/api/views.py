# REST FRAMEWORK
from django.db.models import Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter


# PROJECT
from deposit.api.serializers import DepositSerializer
from deposit.models import Deposit
from envios.models import Envio


@api_view(['GET', ])
@permission_classes((IsAuthenticated, ))
def api_detail_deposit_view(request, pk):
    try:
        deposit = Deposit.objects.get(pk=pk)
    except Deposit.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = DepositSerializer(deposit)
        return Response(serializer.data)


class ApiDepositListView(ListAPIView):
    queryset = Deposit.objects.filter(is_active=True)
    serializer_class = DepositSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = None
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name', 'client__name', )
    # Explicitly specify which fields the API may be ordered against
    ordering_fields = ('name',)
    ordering = ('name',)


class ApiDepositWithEnviosListView(ListAPIView):
    queryset = Deposit.objects.filter(
        is_active=True,
        envio__isnull=False).annotate(
            envios=Count('envio')).order_by('-envios')
    serializer_class = DepositSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = None


class ApiOwnDepositsListView(ListAPIView):
    queryset = Deposit.objects.filter(
        is_active=True, client__isnull=True).order_by('name')
    serializer_class = DepositSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = None


class ApiDepositForEnviosWithCarrierListView(ListAPIView):
    queryset = Deposit.objects.filter(
        is_active=True).annotate(
            envios=Count('envio')).order_by('-envios')
    serializer_class = DepositSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        clients_pk = set(Envio.objects.filter(
            carrier__pk=self.kwargs['carrier_pk'],
            status=Envio.STATUS_MOVING
        ).values_list('client__pk', flat=True))
        return super().get_queryset().filter(
            client__pk__in=clients_pk).distinct()
