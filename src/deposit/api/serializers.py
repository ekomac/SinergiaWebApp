# REST FRAMEWORK
from rest_framework import serializers

# PROJECT
from deposit.models import Deposit
from envios.models import Envio


class DepositSerializer(serializers.ModelSerializer):

    client = serializers.SerializerMethodField('get_client_from_deposit')
    town = serializers.SerializerMethodField('get_town_from_deposit')
    envios = serializers.SerializerMethodField('get_envios_from_deposit')
    envios_tracking_ids = serializers.SerializerMethodField(
        'get_envios_tracking_ids')

    class Meta:
        model = Deposit
        fields = (
            'pk',
            'client',
            'name',
            'is_active',
            'is_sinergia',
            'address',
            'zip_code',
            'town',
            'phone',
            'email',
            'envios',
            'envios_tracking_ids',
        )

    def get_client_from_deposit(self, deposit):
        if deposit.client:
            return {
                'name': deposit.client.name,
                'pk': deposit.client.pk,
            }
        return None

    def get_town_from_deposit(self, deposit):
        if deposit.town:
            return {
                'pk': deposit.town.pk,
                'name': deposit.town.name.title(),
                'partido': {
                    'name': deposit.town.partido.name.title(),
                    'pk': deposit.town.partido.pk,
                },
            }
        return None

    def get_envios_from_deposit(self, deposit):
        return deposit.envio_set.filter(
            status__in=[Envio.STATUS_STILL, Envio.STATUS_NEW]).count()

    def get_envios_tracking_ids(self, deposit):
        if deposit.envio_set.filter(
                status__in=[Envio.STATUS_STILL, Envio.STATUS_NEW]).count() > 0:
            return deposit.envio_set.filter(
                status__in=[Envio.STATUS_STILL, Envio.STATUS_NEW]).values_list(
                'tracking_id', flat=True)
