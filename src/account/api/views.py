# DJANGO
from django.contrib.auth import authenticate
from django.db.models import Count

# REST FRAMEWORK
from rest_framework import status

from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# PROJECT
from account.api.serializers import EmployeeSerializer
from account.models import Account
# LOGIN
# Response: https://gist.github.com/mitchtabian/8e1bde81b3be342853ddfcc45ec0df8a
# URL: http://127.0.0.1:8000/api/account/login


class ObtainAuthTokenView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {}

        email = request.POST.get('username')
        password = request.POST.get('password')
        account = authenticate(email=email, password=password)
        if account:
            try:
                token = Token.objects.get(user=account)
            except Token.DoesNotExist:
                token = Token.objects.create(user=account)
            context['response'] = 'Successfully authenticated.'
            context['pk'] = account.pk
            context['email'] = email.lower()
            context['token'] = token.key
        else:
            context['response'] = 'Error'
            context['error_message'] = 'Credenciales inválidas'

        return Response(context)


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def api_detail_carrier_view(request, pk):
    try:
        account = Account.objects.filter(
            pk=pk, groups__name__in=[
                'Admins', 'Level 1', 'Level 2']).last()
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
        groups__name__in=['Admins', 'Level 1', 'Level 2'],
    ).annotate(
        envios=Count('envios_carried_by')).order_by('-envios').distinct()
    serializer_class = EmployeeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination


class ApiCarrierListView(ListAPIView):
    queryset = Account.objects.filter(
        groups__name__in=['Admins', 'Level 1', 'Level 2'],
        envios_carried_by__isnull=False,
    ).annotate(
        envios=Count('envios_carried_by')).order_by('-envios').distinct()
    serializer_class = EmployeeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
