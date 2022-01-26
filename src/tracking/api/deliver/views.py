from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from tracking.api import consts
from tracking.api.deliver.serializers import (
    DeliveryAttemptSerializer,
)
from tracking.utils.views import get_movement_as_response_data


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def api_delivery_attempt_view(request):
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
                'id': envio.id,
                'full_address': envio.full_address,
                'partido': envio.town.partido.name.title(),
                'status': envio.get_status_display(),
            }
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
