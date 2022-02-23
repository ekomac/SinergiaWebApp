from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from tracking.api import consts
from tracking.api.deliver.serializers import (
    DeliveryAttemptSerializer,
    SuccessfulDeliverySerializer,
)
from tracking.utils.views import get_movement_as_response_data


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_delivery_attempt_view(request):
    print("llegamos al delivery attempt")
    print(request.data)
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk

        # up_file = request.FILES['file']

        serializer = DeliveryAttemptSerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement, envio = serializer.save()
            response_data = get_movement_as_response_data(
                movement, request=request)
            response_data['response'] = consts.CREATE_SUCCESS
            response_data['envio'] = {
                'pk': envio.pk,
                'full_address': envio.full_address,
                'partido': envio.town.partido.name.title(),
                'status': envio.get_status_display(),
                'tracking_id': envio.tracking_id,
            }
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        response_data['response'] = consts.CREATE_ERROR
        response_data['errors'] = serializer.errors
        print("Errors: ", serializer.errors)
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_post_successfull_delivery_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.pk
        serializer = SuccessfulDeliverySerializer(data=data)
        response_data = {}
        if serializer.is_valid():
            movement, envio = serializer.save()
            response_data = {
                'tracking_movement': {
                    'pk': movement.pk,
                    'date_created': movement.date_created,
                    'created_by': {
                        'pk': movement.created_by.pk,
                        'username': movement.created_by.username,
                    },
                    'action': movement.get_action_display(),
                    'result': movement.get_result_display(),
                    'envios_count': movement.envios.count(),
                },
                'response': consts.CREATE_SUCCESS,
                'envio': {
                    'pk': envio.pk,
                    'full_address': envio.full_address,
                    'partido': envio.town.partido.name.title(),
                    'status': envio.get_status_display(),
                    'tracking_id': envio.tracking_id,
                },
            }
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        response_data['response'] = consts.CREATE_ERROR
        response_data['errors'] = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
