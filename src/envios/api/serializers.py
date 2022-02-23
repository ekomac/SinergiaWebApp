# REST FRAMEWORK
from django.utils.dateformat import format
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
    max_delivery_date_timestamp = serializers.SerializerMethodField(
        'get_max_delivery_date_timestamp_from_envio')
    delivery_schedule = serializers.SerializerMethodField(
        'get_delivery_schedule_from_envio')
    receiver = serializers.SerializerMethodField('get_receiver_from_envio')
    tracking_id = serializers.SerializerMethodField(
        'get_tracking_id_from_envio')

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
            'max_delivery_date_timestamp',
            'is_flex',
            'flex_id',
            'delivery_schedule',
            'receiver'
        )

    def get_destination_from_envio(self, envio):
        if envio.destination_ptr is not None:
            street = envio.destination_ptr.street
            remarks = envio.destination_ptr.remarks
            town = str(envio.destination_ptr.town.name).title()
            zipcode = envio.destination_ptr.zipcode
            partido = str(envio.destination_ptr.town.partido.name).title()
            floor_apartment = str(
                envio.destination_ptr.floor_apartment).title()
            return {
                'street': street,
                'remarks': remarks,
                'town': town,
                'zipcode': zipcode,
                'partido': partido,
                'floor_apartment': floor_apartment,
            }
        return None

    def get_status_from_envio(self, envio: Envio):
        return envio.get_status_display()

    def get_client_from_envio(self, envio):
        if envio.client is not None:
            return {
                'pk': envio.client.pk,
                'name': envio.client.name,
            }
        return None

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
            'result': error_movement.get_result_display(),
            'description': error_movement.admin_display()[1],
        }

    def get_max_delivery_date_from_envio(self, envio):
        if envio.max_delivery_date is not None:
            return envio.max_delivery_date.strftime("%d/%m/%Y")
        return None

    def get_max_delivery_date_timestamp_from_envio(self, envio):
        if envio.max_delivery_date is not None:
            return format(envio.max_delivery_date, 'U')
        return None

    def get_delivery_schedule_from_envio(self, envio):
        if envio.delivery_schedule is not None:
            return envio.get_delivery_schedule_display()
        return None

    def get_receiver_from_envio(self, envio):
        if envio.receiver_ptr is not None:
            return {
                'name': envio.receiver_ptr.name,
                'doc': envio.receiver_ptr.doc,
                'phone': envio.receiver_ptr.phone,
            }
        return None

    def get_tracking_id_from_envio(self, envio: Envio):
        return envio.tracking_id if envio.tracking_id is not None else ""


class EnvioStringSerializer(serializers.ModelSerializer):

    data = serializers.SerializerMethodField('get_data')

    class Meta:
        model = Envio
        fields = (
            'pk',
            'data',
        )

    def get_data(self, envio: Envio):
        address = envio.full_address
        client = envio.client.name
        return f"{address}, {client}"
