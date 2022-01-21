# REST FRAMEWORK
from django.db.models import Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter


# PROJECT
from deposit.api.serializers import DepositSerializer
from deposit.models import Deposit


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
    queryset = Deposit.objects.all()
    serializer_class = DepositSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name', 'clien__name', )
    # Explicitly specify which fields the API may be ordered against
    ordering_fields = ('name',)
    ordering = ('name',)


class ApiDepositWithEnviosListView(ListAPIView):
    queryset = Deposit.objects.filter(
        envio__isnull=False).annotate(
            envios=Count('envio')).order_by('-envios')
    serializer_class = DepositSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination


class ApiOwnDepositsListView(ListAPIView):
    queryset = Deposit.objects.filter(client__isnull=True).order_by('name')
    serializer_class = DepositSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
