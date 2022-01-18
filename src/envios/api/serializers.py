# REST FRAMEWORK
from rest_framework import serializers

# PROJECT
from envios.models import Envio


class EnvioSerializer(serializers.ModelSerializer):

    destination = serializers.SerializerMethodField(
        'get_destination_from_envio')
    client = serializers.SerializerMethodField('get_client_from_envio')
    status = serializers.SerializerMethodField('get_status_from_envio')
    deposit = serializers.SerializerMethodField('get_deposit_from_envio')
    carrier = serializers.SerializerMethodField('get_carrier_from_envio')

    class Meta:
        model = Envio
        fields = (
            'pk',
            'destination',
            'status',
            'client',
            'deposit',
            'carrier',
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
