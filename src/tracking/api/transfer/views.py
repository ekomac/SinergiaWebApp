from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from tracking.api import consts
from tracking.api.transfer.serializers import (
    EnviosToTransferFilteredRequestSerializer,
    TransferAllSerializer,
    TransferByEnviosTrackingIdsSerializer,
    TransferByTownsIdsSerializer,
    TransferByPartidosIdsSerializer,
    TransferByZonesIdsSerializer
)
from tracking.utils.views import get_movement_as_response_data


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_transfer_all_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = TransferAllSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_transfer_by_envios_ids_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = TransferByEnviosTrackingIdsSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_transfer_by_towns_ids_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = TransferByTownsIdsSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_transfer_by_partidos_ids_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = TransferByPartidosIdsSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_transfer_by_zones_ids_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = TransferByZonesIdsSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement = serializer.save()
            response_data = get_movement_as_response_data(movement)
            response_data['response'] = consts.CREATE_SUCCESS
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated, ))
def api_envios_for_transfer_preview(request):
    if request.method == 'POST':
        serializer = EnviosToTransferFilteredRequestSerializer(
            data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            data['response'] = consts.SUCCESS
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
