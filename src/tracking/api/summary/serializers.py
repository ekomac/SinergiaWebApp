# Django
from django.utils.dateformat import format

# DRF
from rest_framework import serializers

# TrackingMovement
from tracking.models import TrackingMovement


class TrackingMovementSerializer(serializers.ModelSerializer):

    def get_serializer_context(self):
        context = super(TrackingMovementSerializer,
                        self).get_serializer_context()
        context.update({"request": self.request})
        return context

    from_carrier = serializers.SerializerMethodField('get_from_carrier')
    to_carrier = serializers.SerializerMethodField('get_to_carrier')
    from_deposit = serializers.SerializerMethodField('get_from_deposit')
    to_deposit = serializers.SerializerMethodField('get_to_deposit')
    label = serializers.SerializerMethodField('get_label')
    action = serializers.SerializerMethodField('get_action')
    result = serializers.SerializerMethodField('get_result')
    proof = serializers.SerializerMethodField('get_proof')
    date_created = serializers.SerializerMethodField('get_date_created')
    date_created_timestamp = serializers.SerializerMethodField(
        'get_date_created_timestamp')
    envios_count = serializers.SerializerMethodField(
        'get_envios_count')

    class Meta:
        model = TrackingMovement
        fields = (
            'id',
            'created_by',
            'date_created',
            'date_created_timestamp',
            'action',
            'result',
            'comment',
            'proof',
            'from_carrier',
            'to_carrier',
            'from_deposit',
            'to_deposit',
            'label',
            'envios_count',
        )

    def get_from_carrier(self, tracking_movement):
        if tracking_movement.from_carrier is not None:
            return {
                'pk': tracking_movement.from_carrier.id,
                'username': tracking_movement.from_carrier.username,
                'full_name': tracking_movement.from_carrier.full_name,
                'email': tracking_movement.from_carrier.email,
            }
        return None

    def get_to_carrier(self, tracking_movement):
        if tracking_movement.to_carrier is not None:
            return {
                'pk': tracking_movement.to_carrier.id,
                'username': tracking_movement.to_carrier.username,
                'full_name': tracking_movement.to_carrier.full_name,
                'email': tracking_movement.to_carrier.email,
            }
        return None

    def get_from_deposit(self, tracking_movement):
        if tracking_movement.from_deposit is not None:
            return {
                'pk': tracking_movement.from_deposit.id,
                'name': tracking_movement.from_deposit.name,
            }
        return None

    def get_to_deposit(self, tracking_movement):
        if tracking_movement.to_deposit is not None:
            return {
                'pk': tracking_movement.to_deposit.id,
                'name': tracking_movement.to_deposit.name,
            }
        return None

    def get_label(self, tracking_movement):
        if tracking_movement.label is not None:
            return {
                'key': tracking_movement.label,
                'display': tracking_movement.get_label_display(),
            }
        return None

    def get_action(self, tracking_movement):
        if tracking_movement.action is not None:
            return {
                'key': tracking_movement.action,
                'display': tracking_movement.get_action_display(),
            }
        return None

    def get_result(self, tracking_movement):
        if tracking_movement.result is not None:
            return {
                'key': tracking_movement.result,
                'display': tracking_movement.get_result_display(),
            }
        return None

    def get_created_by(self, tracking_movement):
        if tracking_movement.created_by is not None:
            return {
                'pk': tracking_movement.created_by.id,
                'username': tracking_movement.created_by.username,
                'full_name': tracking_movement.created_by.full_name,
                'email': tracking_movement.created_by.email,
            }
        return None

    def get_proof(self, tracking_movement):
        try:
            if (tracking_movement.proof is not None and
                    tracking_movement.proof.url is not None):
                return self.context['request'].build_absolute_uri(
                    tracking_movement.proof.url)
            return None
        except ValueError:
            return None

    def get_date_created(self, tracking_movement):
        if tracking_movement.date_created is not None:
            return tracking_movement.date_created.strftime("%d/%m/%Y")
        return None

    def get_date_created_timestamp(self, tracking_movement):
        if tracking_movement.date_created is not None:
            return format(tracking_movement.date_created, 'U')
        return None

    def get_envios_count(self, tracking_movement):
        if tracking_movement.envios is not None:
            return tracking_movement.envios.count()
        return 0
