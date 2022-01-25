from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from tracking.api import consts
from tracking.api.withdraw.serializers import (
    WithdrawAllSerializer,
    WithdrawByEnviosIdsSerializer,
    WithdrawByTownsIdsSerializer,
    WithdrawByPartidosIdsSerializer,
    WithdrawByZonesIdsSerializer
)
from tracking.utils.views import get_movement_as_response_data


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_withdraw_all_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = WithdrawAllSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_withdraw_by_envios_ids_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = WithdrawByEnviosIdsSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_withdraw_by_towns_ids_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = WithdrawByTownsIdsSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_withdraw_by_partidos_ids_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = WithdrawByPartidosIdsSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_withdraw_by_zones_ids_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = WithdrawByZonesIdsSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
