# DJANGO
import re
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
from account.api.serializers import (
    AccountPropertiesSerializer,
    EmployeeSerializer)
from account.models import Account

ERROR_INVALID_PASSWORD = "Credenciales inválidas"
ERROR_INVALID_EMAIL = "El email no existe."
PASSWORD_RESET_ERROR_DATA_NOT_RECEIVED = (
    "No se recibieron los datos de la contraseña.")
PASSWORD_RESET_ERROR_PASSWORDS_DONT_MATCH = (
    "Las contraseñas no coinciden.")
PASSWORD_RESET_ERROR_AT_LEAST_EIGHT_CHARS = (
    "La contraseña debe tener al menos 8 caracteres.")
PASSWORD_RESET_ERROR_MAX_TWENTY_CHARS = (
    "La contraseña debe tener menos de 20 caracteres.")
PASSWORD_RESET_ERROR_MUST_CONTAIN_MAYUS = (
    "La contraseña debe tener al menos una mayúscula.")
PASSWORD_RESET_ERROR_MUST_CONTAIN_MINUS = (
    "La contraseña debe tener al menos una minúscula.")
PASSWORD_RESET_ERROR_MUST_CONTAIN_NUM = (
    "La contraseña debe tener al menos un número.")
PASSWORD_RESET_ERROR_MUST_CONTAIN_SPECIAL = (
    "La contraseña debe tener al menos un caracter especial.")


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
                token = Token.objects.filter(user=account)
                new_key = token[0].generate_key()
                token.update(key=new_key)
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
            data['has_to_reset_password'] = account.has_to_reset_password
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
    except Account.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AccountPropertiesSerializer(account)
        data = serializer.data
        data["permission"] = account.groups.first().name
        data["profile_picture_url"] = request.build_absolute_uri(
            account.profile_picture.url) if account.profile_picture else None
        return Response(data)


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
        envios=Count('envios_carried_by')).order_by(
            'first_name', 'last_name', '-envios').distinct()
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


@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def api_reset_password(request):
    if request.method == 'POST':
        data = {}
        email = request.POST.get('email') or request.data.get('email')
        if not Account.objects.filter(
                email=email,
                groups__name__in=settings.ACCESS_EMPLOYEE_APP).exists():
            data['response'] = 'Error'
            data['error_message'] = ERROR_INVALID_EMAIL
            return Response(data)
        user = Account.objects.get(email=email)
        password_1 = request.POST.get(
            "password1", None) or request.data.get('password_1')
        password_2 = request.POST.get(
            "password2", None) or request.data.get('password_2')
        if password_1 is None or password_2 is None:
            data['response'] = 'Error'
            data['error_message'] = PASSWORD_RESET_ERROR_DATA_NOT_RECEIVED
        elif password_1 != password_2:
            data['response'] = 'Error'
            data['error_message'] = PASSWORD_RESET_ERROR_PASSWORDS_DONT_MATCH
        elif len(password_1) < 8:
            data['response'] = 'Error'
            data['error_message'] = PASSWORD_RESET_ERROR_AT_LEAST_EIGHT_CHARS
        elif len(password_1) > 20:
            data['response'] = 'Error'
            data['error_message'] = PASSWORD_RESET_ERROR_MAX_TWENTY_CHARS
        elif not re.search(r'[A-Z]', password_1):
            data['response'] = 'Error'
            data['error_message'] = PASSWORD_RESET_ERROR_MUST_CONTAIN_MAYUS
        elif not re.search(r'[a-z]', password_1):
            data['response'] = 'Error'
            data['error_message'] = PASSWORD_RESET_ERROR_MUST_CONTAIN_MINUS
        elif not re.search(r'[0-9]', password_1):
            data['response'] = 'Error'
            data['error_message'] = PASSWORD_RESET_ERROR_MUST_CONTAIN_NUM
        elif not re.search(r'[@#$%&*.,]', password_1):
            data['response'] = 'Error'
            data['error_message'] = PASSWORD_RESET_ERROR_MUST_CONTAIN_SPECIAL
        if data.get('response') == 'Error':
            print(data)
            return Response(data)
        user.set_password(password_1)
        user.has_to_reset_password = False
        user.save()
        try:
            token = Token.objects.filter(user=user)
            new_key = token[0].generate_key()
            token.update(key=new_key)
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
        data['response'] = 'Se actualizó la contraseña.'
        data['pk'] = user.pk
        data['email'] = email.lower()
        data['token'] = token.key
        data['first_name'] = user.first_name
        data['last_name'] = user.last_name
        data['username'] = user.username
        data['full_name'] = user.full_name
        data['permission'] = user.groups.first().name
        data['has_to_reset_password'] = user.has_to_reset_password
        data['profile_picture_url'] = None
        if (user.profile_picture and
                user.profile_picture.url is not None):
            data['profile_picture_url'] = request.build_absolute_uri(
                user.profile_picture.url)
        return Response(data=data, status=status.HTTP_200_OK)
