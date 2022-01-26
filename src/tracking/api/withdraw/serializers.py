from rest_framework import serializers

from envios.models import Envio
from places.models import Partido, Town, Zone
from tracking.models import TrackingMovement
from tracking.utils.withdraw import (
    withdraw_all,
    withdraw_by_envios_ids,
    withdraw_by_partidos_ids,
    withdraw_by_towns_ids,
    withdraw_by_zones_ids
)


class BaseWithdrawSerializer(serializers.ModelSerializer):

    statuses = [Envio.STATUS_NEW, Envio.STATUS_STILL]

    def check_deposit_has_envios(self, data):
        from_deposit = data['from_deposit']
        if from_deposit.envio_set.filter(
            status__in=[Envio.STATUS_STILL, Envio.STATUS_NEW]
        ).count() == 0:
            raise serializers.ValidationError(
                {"response": "Deposit hasn't got any Envíos."})

    def extra_validation_check(self, data):
        pass

    def validation(self, data):
        self.check_deposit_has_envios(data)
        self.extra_validation_check(data)
        return data


class WithdrawAllSerializer(BaseWithdrawSerializer):
    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_deposit', 'to_carrier',)
        extra_kwargs = {
            'created_by': {'required': True, },
            'from_deposit': {'required': True, },
            'to_carrier': {'required': True, },
        }

    def save(self):
        author = self.validated_data['created_by']
        from_deposit = self.validated_data['from_deposit']
        to_carrier = self.validated_data['to_carrier']
        return withdraw_all(author, from_deposit, to_carrier)


class WithdrawByEnviosIdsSerializer(BaseWithdrawSerializer):

    envios_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_deposit', 'to_carrier', 'envios_ids',)
        extra_kwargs = {
            'created_by': {'required': True, },
            'from_deposit': {'required': True, },
            'to_carrier': {'required': True, },
            'envios_ids': {'required': True, },
        }

    def extra_validation_check(self, data):
        from_deposit = data['from_deposit']
        pk = from_deposit.pk
        envios_at_deposit = from_deposit.envio_set.filter(
            status__in=self.statuses,
        ).values_list('pk', flat=True)
        envios_at_deposit_count = len(envios_at_deposit)
        envios_ids = data['envios_ids']
        if len(envios_ids) == 0:
            msg = "'envios_ids' can't be empty."
            raise serializers.ValidationError({"response": msg})
        if len(envios_ids) > envios_at_deposit_count:
            msg = "There are only %s Envíos at the deposit with id=%s." % (
                envios_at_deposit_count, pk)
            raise serializers.ValidationError({"response": msg})
        if set(envios_ids).issubset(envios_at_deposit):
            msg = (
                "Some of the Envíos with ids %s don't exist or "
                "are not at the deposit with id=%s."
            ) % (envios_ids, pk)
            raise serializers.ValidationError({"response": msg})

    def save(self):
        author = self.validated_data['created_by']
        from_deposit = self.validated_data['from_deposit']
        to_carrier = self.validated_data['to_carrier']
        envios_ids = self.validated_data['envios_ids']
        return withdraw_by_envios_ids(
            author, from_deposit, to_carrier, *envios_ids)


class WithdrawByTownsIdsSerializer(BaseWithdrawSerializer):

    towns_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_deposit', 'to_carrier', 'towns_ids',)
        extra_kwargs = {
            'created_by': {'required': True, },
            'from_deposit': {'required': True, },
            'to_carrier': {'required': True, },
            'towns_ids': {'required': True, },
        }

    def extra_validation_check(self, data):
        towns_ids = data['towns_ids']
        from_deposit = data['from_deposit']
        pk = from_deposit.pk
        towns_ids_on_deposit = Town.objects.filter(
            destination__receiver__envio__deposit__id=pk,
            destination__receiver__envio__status__in=self.statuses,
        ).values_list('id', flat=True).distinct()
        if not set(towns_ids, pk).issubset(towns_ids_on_deposit):
            msg = (
                "Some of the Towns with given ids %s don't exist or"
                "don't reach out to Envios at Deposit with id=%s."
            ) % (towns_ids, pk)
            raise serializers.ValidationError({"response": msg})

    def save(self):
        author = self.validated_data['created_by']
        from_deposit = self.validated_data['from_deposit']
        to_carrier = self.validated_data['to_carrier']
        towns_ids = self.validated_data['towns_ids']
        return withdraw_by_towns_ids(
            author, from_deposit, to_carrier, *towns_ids)


class WithdrawByPartidosIdsSerializer(BaseWithdrawSerializer):

    partidos_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_deposit', 'to_carrier', 'partidos_ids',)
        extra_kwargs = {
            'created_by': {'required': True, },
            'from_deposit': {'required': True, },
            'carrto_carrierier': {'required': True, },
            'partidos_ids': {'required': True, },
        }

    def extra_validation_check(self, data):
        partidos_ids = data['partidos_ids']
        from_deposit = data['from_deposit']
        pk = from_deposit.pk
        partidos_ids_on_deposit = Partido.objects.filter(
            town__destination__receiver__envio__deposit__id=pk,
            town__destination__receiver__envio__status__in=self.statuses,
        ).values_list('id', flat=True).distinct()
        if not set(partidos_ids).issubset(partidos_ids_on_deposit):
            msg = (
                "Some of the Partidos with given ids %s don't exist or"
                "don't reach out to Envíos at Deposit with id=%s."
            ) % (partidos_ids, pk)
            raise serializers.ValidationError({"response": msg})

    def save(self):
        author = self.validated_data['created_by']
        from_deposit = self.validated_data['from_deposit']
        to_carrier = self.validated_data['to_carrier']
        partidos_ids = self.validated_data['partidos_ids']
        return withdraw_by_partidos_ids(
            author, from_deposit, to_carrier, *partidos_ids)


class WithdrawByZonesIdsSerializer(BaseWithdrawSerializer):

    zones_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_deposit', 'to_carrier', 'zones_ids',)
        extra_kwargs = {
            'created_by': {'required': True, },
            'from_deposit': {'required': True, },
            'to_carrier': {'required': True, },
            'zones_ids': {'required': True, },
        }

    def extra_validation_check(self, data):
        zones_ids = data['zones_ids']
        from_deposit = data['from_deposit']
        pk = from_deposit.pk
        base_filter_str = 'partido__town__destination__receiver__envio__'
        filters = {
            base_filter_str + 'deposit__id': pk,
            base_filter_str + 'status__in': self.statuses,
        }
        zones_ids_on_deposit = Zone.objects.filter(
            **filters).values_list('id', flat=True).distinct()
        if not set(zones_ids).issubset(zones_ids_on_deposit):
            msg = (
                "Some of the Zones with given ids %s don't exist or"
                "don't reach out to Envíos at Deposit with id=%s."
            ) % (zones_ids, pk)
            raise serializers.ValidationError({"response": msg})

    def save(self):
        author = self.validated_data['created_by']
        from_deposit = self.validated_data['from_deposit']
        to_carrier = self.validated_data['to_carrier']
        zones_ids = self.validated_data['zones_ids']
        return withdraw_by_zones_ids(
            author, from_deposit, to_carrier, *zones_ids)
