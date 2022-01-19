from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter

from tracking.api.serializers import WithdrawAllSerializer, WithdrawByIdsSerializer
from tracking.api import consts
from tracking.api import actions


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def api_withdraw_all_view(request):

    if request.method == 'POST':

        data = request.data
        data._mutable = True
        data['created_by'] = request.user.pk
        data._mutable = False
        serializer = WithdrawAllSerializer(data=data)

        data = {}
        if serializer.is_valid():
            movement = serializer.save()
            data = get_movement_as_response_data(movement)
            data['response'] = consts.CREATE_SUCCESS
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def api_withdraw_by_ids_view(request):

    if request.method == 'POST':

        data = request.data
        data._mutable = True
        data['created_by'] = request.user.pk
        data._mutable = False
        serializer = WithdrawByIdsSerializer(data=data)

        data = {}
        if serializer.is_valid():
            movement = serializer.save()
            data = get_movement_as_response_data(movement)
            data['response'] = consts.CREATE_SUCCESS
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_movement_as_response_data(movement):
    data = {
        'pk': movement.pk,
        'created_by': {
            'pk': movement.created_by.pk,
            'username': movement.created_by.username,
        },
        'action': movement.get_action_display(),
        'result': movement.get_result_display(),
        'envios_count': movement.envios.count(),
    }
    return data
