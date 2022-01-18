# DJANGO
from django.db.models import Count

# REST FRAMEWORK
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter


# PROJECT
from account.api.serializers import CarrierSerializer
from account.models import Account


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_detail_carrier_view(request, pk):
    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = CarrierSerializer(account)
        return Response(serializer.data)


class ApiCarrierListView(ListAPIView):
    queryset = Account.objects.filter(
        groups__name__in=['Admins', 'EmployeeTier1', 'EmployeeTier2'],
    ).annotate(envios=Count('Carrier')).distinct()
    serializer_class = CarrierSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('first_name', 'last_name', 'username', 'email')
    # Explicitly specify which fields the API may be ordered against
    ordering_fields = ('last_name', 'first_name',
                       'envios', 'username', 'email',)
    ordering = ('-envios', 'first_name', 'last_name', 'username', 'email')
