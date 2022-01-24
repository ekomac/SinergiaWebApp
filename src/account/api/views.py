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


# PROJECT
from account.api.serializers import EmployeeSerializer
from account.models import Account


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def api_detail_carrier_view(request, pk):
    try:
        account = Account.objects.filter(
            pk=pk, groups__name__in=[
                'Admins', 'EmployeeTier1', 'EmployeeTier2']).last()
        if account is None:
            return Response(
                data={
                    'response': 'No se encontró la cuenta con id {}.'.format(
                        account.pk)
                },
                status=status.HTTP_404_NOT_FOUND)
    except Account.DoesNotExist or ValueError:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response(
            data={
                'response': "La cuenta de empleado con id {} no existe".format(
                    pk)},
            status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = EmployeeSerializer(account)
        return Response(serializer.data)


class ApiEmployeesWithEnviosListView(ListAPIView):
    queryset = Account.objects.filter(
        groups__name__in=['Admins', 'EmployeeTier1', 'EmployeeTier2'],
    ).annotate(envios=Count('Carrier')).order_by('-envios').distinct()
    serializer_class = EmployeeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination


class ApiCarrierListView(ListAPIView):
    queryset = Account.objects.filter(
        groups__name__in=['Admins', 'EmployeeTier1', 'EmployeeTier2'],
        Carrier__isnull=False,
    ).annotate(envios=Count('Carrier')).order_by('-envios').distinct()
    serializer_class = EmployeeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
