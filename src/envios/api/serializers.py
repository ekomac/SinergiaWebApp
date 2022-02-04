# REST FRAMEWORK
from rest_framework import serializers

# PROJECT
from envios.models import Envio
from tracking.models import TrackingMovement


class EnvioSerializer(serializers.ModelSerializer):

    destination = serializers.SerializerMethodField(
        'get_destination_from_envio')
    client = serializers.SerializerMethodField('get_client_from_envio')
    status = serializers.SerializerMethodField('get_status_from_envio')
    deposit = serializers.SerializerMethodField('get_deposit_from_envio')
    carrier = serializers.SerializerMethodField('get_carrier_from_envio')
    error = serializers.SerializerMethodField('get_error_from_envio')
    max_delivery_date = serializers.SerializerMethodField(
        'get_max_delivery_date_from_envio')

    class Meta:
        model = Envio
        fields = (
            'pk',
            'tracking_id',
            'destination',
            'status',
            'client',
            'deposit',
            'carrier',
            'error',
            'charge',
            'max_delivery_date',
            'is_flex',
            'flex_id',
            'delivery_schedule',
        )

    def get_destination_from_envio(self, envio):
        return envio.destination_ptr.full_address

    def get_client_from_envio(self, envio):
        if envio.client is not None:
            return {
                'pk': envio.client.pk,
                'username': envio.client.name,
            }
        return None

    def get_status_from_envio(self, envio):
        return envio.get_status_display()

    def get_deposit_from_envio(self, envio):
        if envio.deposit is not None:
            return {
                'pk': envio.deposit.pk,
                'name': envio.deposit.name,
            }
        return None

    def get_carrier_from_envio(self, envio):
        if envio.carrier is not None:
            return {
                'pk': envio.carrier.pk,
                'username': envio.carrier.username,
            }
        return None

    def get_error_from_envio(self, envio):
        error_results = [
            TrackingMovement.RESULT_REJECTED_AT_DESTINATION, TrackingMovement.
            RESULT_REPROGRAMED, TrackingMovement.RESULT_NO_ANSWER,
            TrackingMovement.RESULT_TRANSFERED, TrackingMovement.
            RESULT_COLLECTED, TrackingMovement.RESULT_OTHER, ]
        if not TrackingMovement.objects.filter(
                envios__in=[envio], result__in=error_results).exists():
            return ""
        error_movement: TrackingMovement = TrackingMovement.objects.filter(
            envios__in=[envio], result__in=error_results).last()
        return {
            'pk': error_movement.pk,
            'result': error_movement.result,
            'description': error_movement.admin_display(),
        }

    def get_max_delivery_date_from_envio(self, envio):
        if envio.max_delivery_date is not None:
            return envio.max_delivery_date.strftime("%d/%m/%Y")
        return None
