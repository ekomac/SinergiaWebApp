from rest_framework import serializers
from tracking.models import TrackingMovement


class TrackingMovementSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrackingMovement
        # fields = (
        #     'envios',
        #     'created_by',
        #     'label',
        #     'action',
        #     'result',
        #     'comment',
        #     'date_created',
        #     'proof_url',
        #     'from_carrier',
        #     'to_carrier',
        #     'from_deposit',
        #     'to_deposit',
        #     'summary',
        # )
