from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from mobile_app.api.serializers import MobileAppSerializer
from mobile_app.models import MobileApp


@api_view(['GET', ])
@permission_classes((IsAuthenticated, ))
def api_latest_mobile_app_view(request):
    try:
        mobile_app = MobileApp.objects.last()
    except MobileApp.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = MobileAppSerializer(mobile_app)
        return Response(serializer.data)
    return Response(status=status.HTTP_404_NOT_FOUND)
