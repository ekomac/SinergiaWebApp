# Django
from datetime import datetime
from django.db.models import Q

# DRF
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

# Project
from tracking.api.summary.serializers import TrackingMovementSerializer
from tracking.models import TrackingMovement


class TrackingMovementsForCarrierListView(ListAPIView):
    queryset = TrackingMovement.objects.all().order_by('-date_created')
    serializer_class = TrackingMovementSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = super(
            TrackingMovementsForCarrierListView, self).get_queryset()
        carrier_pk = self.kwargs.get('carrier_pk', None)
        if carrier_pk is not None:
            queryset = queryset.filter(
                Q(from_carrier__id=carrier_pk) | Q(
                    to_carrier__id=carrier_pk) | Q(
                        created_by__id=carrier_pk)
            ).distinct()
        filters = {}
        params = self.request.query_params
        if params.get('result', None) is not None:
            result = params.get('result')
            filters['result'] = result
        if params.get('max_date', None) is not None:
            max_date = int(params.get('max_date'))
            max_date = datetime.fromtimestamp(max_date)
            filters['date_created__lte'] = max_date
        if params.get('min_date', None) is not None:
            min_date = int(params.get('min_date'))
            min_date = datetime.fromtimestamp(min_date)
            filters['date_created__gte'] = min_date
        print(queryset.filter(**filters).distinct())
        return queryset.filter(**filters).distinct()
