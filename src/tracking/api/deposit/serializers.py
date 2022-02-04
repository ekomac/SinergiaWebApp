from rest_framework import serializers

from envios.models import Envio
from places.models import Partido, Town, Zone
from tracking.models import TrackingMovement
from tracking.utils.deposit import (
    deposit_all,
    deposit_by_envios_tracking_ids,
    deposit_by_partidos_ids,
    deposit_by_towns_ids,
    deposit_by_zones_ids
)


class BaseDepositSerializer(serializers.ModelSerializer):

    status = Envio.STATUS_MOVING

    def check_carrier_is_carrier(self, data):
        from_carrier = data['from_carrier']
        envios_count = from_carrier.envios_carried_by.filter(
            status=self.status).count()
        if envios_count == 0:
            id = from_carrier.id
            msg = "Account with id %s isn't carrying any Envíos." % id
            raise serializers.ValidationError({"response": msg})

    def extra_validation_check(self, data):
        pass

    def validate(self, data):
        self.check_carrier_is_carrier(data)
        self.extra_validation_check(data)
        return data


class DepositAllSerializer(BaseDepositSerializer):
    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_carrier', 'to_deposit',)
        extra_kwargs = {
            'created_by': {'required': True, },
            'from_carrier': {'required': True, },
            'to_deposit': {'required': True, },
        }

    def save(self):
        author = self.validated_data['created_by']
        to_deposit = self.validated_data['to_deposit']
        from_carrier = self.validated_data['from_carrier']
        return deposit_all(author, from_carrier, to_deposit)


class DepositByEnviosTrackingIdsSerializer(BaseDepositSerializer):

    envios_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_carrier',
                  'to_deposit', 'envios_tracking_ids',)
        extra_kwargs = {
            'created_by': {'required': True, },
            'from_carrier': {'required': True, },
            'to_deposit': {'required': True, },
            'envios_tracking_ids': {'required': True, },
        }

    def extra_validation_check(self, data):
        from_carrier = data['from_carrier']
        pk = from_carrier.pk
        envios_with_carrier = from_carrier.envios_carried_by.filter(
            status=self.status
        ).values_list('pk', flat=True)
        envios_with_carrier_count = len(envios_with_carrier)
        envios_tracking_ids = data['envios_ids']
        if len(envios_tracking_ids) == 0:
            msg = "'envios_tracking_ids' can't be empty."
            raise serializers.ValidationError({"response": msg})
        if len(envios_tracking_ids) > envios_with_carrier_count:
            msg = "There are only %s Envíos with the Carrier with id=%s." % (
                envios_with_carrier_count, pk)
            raise serializers.ValidationError({"response": msg})
        if set(envios_tracking_ids).issubset(envios_with_carrier):
            msg = (
                "Some of the Envíos with ids %s don't exist "
                "or aren't carried by the Account with id=%s."
            ) % (envios_tracking_ids, pk)

    def save(self):
        author = self.validated_data['created_by']
        from_carrier = self.validated_data['from_carrier']
        to_deposit = self.validated_data['to_deposit']
        envios_tracking_ids = self.validated_data['envios_tracking_ids']
        return deposit_by_envios_tracking_ids(
            author, from_carrier, to_deposit, *envios_tracking_ids)


class DepositByTownsIdsSerializer(BaseDepositSerializer):
    towns_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_carrier', 'to_deposit', 'towns_ids')
        extra_kwargs = {
            'created_by': {'required': True, },
            'from_carrier': {'required': True, },
            'to_deposit': {'required': True, },
            'towns_ids': {'required': True, },
        }

    def extra_validation_check(self, data):
        towns_ids = data['towns_ids']
        from_carrier = data['from_carrier']
        pk = from_carrier.pk
        towns_ids_on_carrier = Town.objects.filter(
            destination__receiver__envio__carrier__id=pk,
            destination__receiver__envio__status=self.status,
        ).values_list('pk', flat=True).distinct()
        if not set(towns_ids).issubset(towns_ids_on_carrier):
            msg = (
                "Some of the Towns with given ids %s don't exist or don't "
                "reach out to Envios carried by Account with id=%s."
            ) % (towns_ids, pk)
            raise serializers.ValidationError({"response": msg})

    def save(self):
        author = self.validated_data['created_by']
        from_carrier = self.validated_data['from_carrier']
        to_deposit = self.validated_data['to_deposit']
        towns_ids = self.validated_data['towns_ids']
        return deposit_by_towns_ids(
            author, from_carrier, to_deposit, *towns_ids)


class DepositByPartidosIdsSerializer(BaseDepositSerializer):

    partidos_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_carrier', 'to_deposit', 'partidos_ids')
        extra_kwargs = {
            'created_by': {'required': True, },
            'from_carrier': {'required': True, },
            'to_deposit': {'required': True, },
            'partidos_ids': {'required': True, },
        }

    def extra_validations_check(self, data):
        partidos_ids = data['partidos_ids']
        from_carrier = data['from_carrier']
        pk = from_carrier.pk
        partidos_ids_on_carrier = Partido.objects.filter(
            town__destination__receiver__envio__carrier__id=pk,
            town__destination__receiver__envio__status=self.status,
        ).values_list('pk', flat=True).distinct()
        if not set(partidos_ids).issubset(partidos_ids_on_carrier):
            msg = (
                "Some of the Partidos with given ids %s don't exist or don't "
                "reach out to Envios carried by Account with id=%s."
            ) % (partidos_ids, pk)
            raise serializers.ValidationError({"response": msg})

    def save(self):
        author = self.validated_data['created_by']
        from_carrier = self.validated_data['from_carrier']
        to_deposit = self.validated_data['to_deposit']
        partidos_ids = self.validated_data['partidos_ids']
        return deposit_by_partidos_ids(
            author, from_carrier, to_deposit, *partidos_ids)


class DepositByZonesIdsSerializer(BaseDepositSerializer):

    zones_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_carrier', 'to_deposit', 'zones_ids',)
        extra_kwargs = {
            'created_by': {'required': True, },
            'from_carrier': {'required': True, },
            'to_deposit': {'required': True, },
            'zones_ids': {'required': True, },
        }

    def extra_validations_check(self, data):
        zones_ids = data['zones_ids']
        from_carrier = data['from_carrier']
        pk = from_carrier.pk
        base_filter_srt = 'partido__town__destination__receiver__envio__'
        filters = {
            base_filter_srt + 'carrier__id': pk,
            base_filter_srt + 'status': self.status,
        }
        zones_ids_on_carrier = Zone.objects.filter(
            **filters).values_list('pk', flat=True).distinct()
        if not set(zones_ids).issubset(zones_ids_on_carrier):
            msg = (
                "Some of the Zones with given ids %s don't exist or don't "
                "reach out to Envios carried by Account with id=%s."
            ) % (zones_ids, pk)
            raise serializers.ValidationError({"response": msg})

    def save(self):
        author = self.validated_data['created_by']
        from_carrier = self.validated_data['from_carrier']
        to_deposit = self.validated_data['to_deposit']
        zones_ids = self.validated_data['zones_ids']
        return deposit_by_zones_ids(
            author, from_carrier, to_deposit, *zones_ids)
