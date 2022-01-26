from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from tracking.api import consts
from tracking.api.deposit.serializers import (
    DepositAllSerializer,
    DepositByEnviosIdsSerializer,
    DepositByTownsIdsSerializer,
    DepositByPartidosIdsSerializer,
    DepositByZonesIdsSerializer
)
from tracking.utils.views import get_movement_as_response_data


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_deposit_all_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = DepositAllSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_deposit_by_envios_ids_view(request):
    print(request.__dict__)
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = DepositByEnviosIdsSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_deposit_by_towns_ids_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = DepositByTownsIdsSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_deposit_by_partidos_ids_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = DepositByPartidosIdsSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_deposit_by_zones_ids_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = DepositByZonesIdsSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
