# REST FRAMEWORK
from rest_framework import serializers

# PROJECT
from account.models import Account


class CarrierSerializer(serializers.ModelSerializer):

    envios = serializers.SerializerMethodField('get_envios_from_carrier')
    full_name = serializers.SerializerMethodField('get_full_name_from_carrier')

    class Meta:
        model = Account
        fields = (
            'pk',
            'email',
            'username',
            'full_name',
            'first_name',
            'last_name',
            'envios',
        )

    def get_envios_from_carrier(self, account):
        return account.Carrier.count()

    def get_full_name_from_carrier(self, account):
        return account.full_name
