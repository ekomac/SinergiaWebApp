from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter

from account.models import Account
from places.models import Town
from places.api import TownSerializer


class ApiTownsOfEnviosInDepositListView(ListAPIView):
    queryset = Town.objects.filter(
        envio__isnull=False).annotate(
            envios=Count('envio')).order_by('-envios')
    serializer_class = TownSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
