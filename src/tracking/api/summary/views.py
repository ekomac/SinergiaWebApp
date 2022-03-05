# Django
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
                Q(from_carrier__id=carrier_pk) | Q(to_carrier__id=carrier_pk),
            ).distinct()
        filters = {}
        params = self.request.query_params
        if self.request.query_params.get('max_date', None) is not None:
            filters['date_created__lte'] = params.get('max_date')
        if self.request.query_params.get('min_date', None) is not None:
            filters['date_created__gte'] = params.get('min_date')
        return queryset.filter(**filters).distinct()
