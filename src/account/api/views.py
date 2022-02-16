# DJANGO
from django.conf import settings
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

ERROR_INVALID_PASSWORD = "Credenciales inválidas"
ERROR_INVALID_EMAIL = "El email no existe."


class ObtainAuthTokenView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = {}
        email = request.POST.get('username') or request.data.get('username')
        if not Account.objects.filter(
                email=email,
                groups__name__in=settings.ACCESS_EMPLOYEE_APP).exists():
            data['response'] = 'Error'
            data['error_message'] = ERROR_INVALID_EMAIL
            return Response(data)
        password = request.POST.get('password') or request.data.get('password')
        account = authenticate(email=email, password=password)
        if account:
            try:
                token = Token.objects.get(user=account)
            except Token.DoesNotExist:
                token = Token.objects.create(user=account)
            data['response'] = 'Successfully authenticated.'
            data['pk'] = account.pk
            data['email'] = email.lower()
            data['token'] = token.key
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['username'] = account.username
            data['full_name'] = account.full_name
            data['permission'] = account.groups.first().name
            data['profile_picture_url'] = None
            if (account.profile_picture and
                    account.profile_picture.url is not None):
                data['profile_picture_url'] = request.build_absolute_uri(
                    account.profile_picture.url)
        else:
            data['response'] = 'Error'
            data['error_message'] = ERROR_INVALID_PASSWORD
        return Response(data)


@api_view(['GET', ])
@permission_classes((IsAuthenticated, ))
def api_account_properties_view(request):

    try:
        account = request.user
        print(account)
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EmployeeSerializer(account)
        return Response(serializer.data)


@api_view(['GET', ])
@permission_classes((IsAuthenticated, ))
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
        if request.method == 'GET':
            serializer = EmployeeSerializer(account)
            data = serializer.data
            data['response'] = 'Successfully authenticated.'
            data['pk'] = account.pk
            data['email'] = account.email.lower()
            data['token'] = account.token.key
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['username'] = account.username
            data['full_name'] = account.full_name
            data['profile_picture_url'] = None
            if (account.profile_picture and
                    account.profile_picture.url is not None):
                data['profile_picture_url'] = request.build_absolute_uri(
                    account.profile_picture.url)
            return Response(data, status=status.HTTP_200_OK)
    except Account.DoesNotExist or ValueError:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response(
            data={
                'response': "La cuenta de empleado con id {} no existe".format(
                    pk)},
            status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def api_detail_account_view(request, pk):
    try:
        account = Account.objects.filter(
            pk=pk, groups__name__in=[
                'Admins', 'Level 1', 'Level 2']).last()
        if account is None:
            print("Account doesn't exist!!!")
            data = {'response': 'No se encontró la cuenta con id %s.' % pk},
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        if request.method == 'GET':
            serializer = EmployeeSerializer(account)
            data = serializer.data
            data['response'] = 'Successfully authenticated.'
            data['pk'] = account.pk
            data['email'] = account.email.lower()
            data['token'] = Token.objects.get(user=account).key
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['username'] = account.username
            data['full_name'] = account.full_name
            data['permission'] = account.groups.first().name
            data['profile_picture_url'] = None
            if account.profile_picture:
                if account.profile_picture.url is not None:
                    data['profile_picture_url'] = request.build_absolute_uri(
                        account.profile_picture.url)
            return Response(data, status=status.HTTP_200_OK)
    except Account.DoesNotExist:
        print("Account doesn't exist")
        return Response(status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        data = {'response': "La cuenta de empleado con id %s no existe" % pk}
        return Response(
            data=data,
            status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def api_check_app_state_view(request, pk: int = 0):
    try:
        account = Account.objects.filter(
            pk=pk, groups__name__in=['Admins', 'Level 1', 'Level 2']).last()
        if account is None:
            data = {'response': 'No se encontró la cuenta con id %s.' % pk},
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        if request.method == 'GET':
            data['response'] = 'User found.'
            data['pk'] = account.pk
            data['has_access_denied'] = account.has_access_denied
            return Response(data, status=status.HTTP_200_OK)
    except Account.DoesNotExist:
        print("Account doesn't exist")
        return Response(status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        data = {'response': "La cuenta de empleado con id %s no existe" % pk}
        return Response(data=data, status=status.HTTP_404_NOT_FOUND)


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
