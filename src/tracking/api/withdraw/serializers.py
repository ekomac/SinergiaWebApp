from rest_framework import serializers

from envios.models import Envio
from tracking.models import TrackingMovement
from tracking.utils.withdraw import (
    withdraw_all,
    withdraw_by_envios_ids,
    withdraw_by_partidos_ids,
    withdraw_by_towns_ids,
    withdraw_by_zones_ids
)


class BaseWithdrawSerializer(serializers.ModelSerializer):
    def check_deposit_has_envios(self, deposit):
        if deposit.envio_set.filter(
            status__in=[Envio.STATUS_STILL, Envio.STATUS_NEW]
        ).count() == 0:
            raise serializers.ValidationError(
                {"response": "Deposit hasn't got any Envíos."})


class WithdrawAllSerializer(BaseWithdrawSerializer):
    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'carrier', 'deposit',)
        extra_kwargs = {
            'carrier': {'required': True, },
            'deposit': {'required': True, },
        }

    def save(self):
        author = self.validated_data['created_by']
        deposit = self.validated_data['deposit']
        self.check_deposit_has_envios(deposit)
        carrier = self.validated_data['carrier']
        return withdraw_all(author, deposit, carrier)


class WithdrawByEnviosIdsSerializer(BaseWithdrawSerializer):

    envios_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'carrier', 'deposit', 'envios_ids',)
        extra_kwargs = {
            'carrier': {'required': True, },
            'deposit': {'required': True, },
            'envios_ids': {'required': True, },
        }

    def save(self):
        author = self.validated_data['created_by']
        deposit = self.validated_data['deposit']
        self.check_deposit_has_envios(deposit)
        carrier = self.validated_data['carrier']
        envios_ids = self.validated_data['envios_ids']

        if deposit.envio_set.filter(
                pk__in=envios_ids).count() != len(envios_ids):
            raise serializers.ValidationError(
                {"response": "Some of the Envíos with given ids " +
                    "{} don't exist or aren't at the deposit {}.".format(
                        envios_ids, deposit)
                 }
            )
        return withdraw_by_envios_ids(
            author, deposit, carrier, *envios_ids)


class WithdrawByTownsIdsSerializer(BaseWithdrawSerializer):
    towns_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'carrier', 'deposit', 'towns_ids',)
        extra_kwargs = {
            'carrier': {'required': True, },
            'deposit': {'required': True, },
            'towns_ids': {'required': True, },
        }

    def save(self):
        author = self.validated_data['created_by']
        deposit = self.validated_data['deposit']
        self.check_deposit_has_envios(deposit)
        carrier = self.validated_data['carrier']
        towns_ids = self.validated_data['towns_ids']

        if deposit.envio_set.filter(
                town__id__in=towns_ids).count() != len(towns_ids):
            raise serializers.ValidationError(
                {"response": "Some of the Towns with given ids {} ".format(
                    towns_ids
                ) + "don't correspond to Envíos at the deposit {}.".format(
                    deposit)
                }
            )
        return withdraw_by_towns_ids(author, deposit, carrier, *towns_ids)


class WithdrawByPartidosIdsSerializer(BaseWithdrawSerializer):

    partidos_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'carrier', 'deposit', 'partidos_ids',)
        extra_kwargs = {
            'carrier': {'required': True, },
            'deposit': {'required': True, },
            'partidos_ids': {'required': True, },
        }

    def save(self):
        author = self.validated_data['created_by']
        deposit = self.validated_data['deposit']
        self.check_deposit_has_envios(deposit)
        carrier = self.validated_data['carrier']
        partidos_ids = self.validated_data['partidos_ids']

        if deposit.envio_set.filter(
                town__partido__id__in=partidos_ids
        ).count() != len(partidos_ids):
            raise serializers.ValidationError(
                {"response": "Some of the Partidos with given ids" +
                 " {} don't correspond to Towns ".format(partidos_ids) +
                 "of Envíos at the deposit {}.".format(deposit)}
            )
        return withdraw_by_partidos_ids(
            author, deposit, carrier, *partidos_ids)


class WithdrawByZonesIdsSerializer(BaseWithdrawSerializer):

    zones_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'carrier', 'deposit', 'zones_ids',)
        extra_kwargs = {
            'carrier': {'required': True, },
            'deposit': {'required': True, },
            'zones_ids': {'required': True, },
        }

    def save(self):
        author = self.validated_data['created_by']
        deposit = self.validated_data['deposit']
        self.check_deposit_has_envios(deposit)
        carrier = self.validated_data['carrier']
        zones_ids = self.validated_data['zones_ids']

        if deposit.envio_set.filter(
                town__partido__zone__id__in=zones_ids
        ).count() != len(zones_ids):
            raise serializers.ValidationError(
                {"response": "Some of the Zones with given ids" +
                 " {} don't correspond to Partidos of Towns ".format(
                     zones_ids
                 ) + "of Envíos at the deposit {}.".format(deposit)}
            )
        return withdraw_by_zones_ids(author, deposit, carrier, *zones_ids)
