from rest_framework import serializers

from envios.models import Envio
from places.models import Partido, Town, Zone
from tracking.models import TrackingMovement
from tracking.utils.withdraw import (
    withdraw_all,
    withdraw_by_envios_tracking_ids,
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

    def validate(self, data):
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


class WithdrawByEnviosTrackingIdsSerializer(BaseWithdrawSerializer):

    envios_tracking_ids = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True, allow_empty=False)

    overflow_enabled = serializers.BooleanField(default=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_deposit',
                  'to_carrier', 'envios_tracking_ids', 'overflow_enabled')
        extra_kwargs = {
            'created_by': {'required': True, },
            'from_deposit': {'required': True, },
            'to_carrier': {'required': True, },
            'envios_tracking_ids': {'required': True, },
            'overflow_enabled': {'required': False, },
        }

    def extra_validation_check(self, data):
        from_deposit = data['from_deposit']
        pk = from_deposit.pk
        envios_at_deposit = from_deposit.envio_set.filter(
            status__in=self.statuses,
        ).values_list('tracking_id', flat=True)
        envios_at_deposit_count = len(envios_at_deposit)
        envios_tracking_ids = data['envios_tracking_ids']
        if len(envios_tracking_ids) == 0:
            msg = "'envios_tracking_ids' can't be empty."
            raise serializers.ValidationError({"response": msg})
        overflow_enabled = data['overflow_enabled']
        print("overflow_enabled", overflow_enabled)
        if not overflow_enabled:
            if len(envios_tracking_ids) > envios_at_deposit_count:
                s1 = "There are only %s Envíos at the deposit with id=%s." % (
                    envios_at_deposit_count, pk)
                s2 = "You've sent %s" % (len(envios_tracking_ids))
                full_msg = f'{s1} {s2}'
                raise serializers.ValidationError({"response": full_msg})
            print("set", set(envios_tracking_ids))
            print("envios_at_deposit", envios_at_deposit)
            if set(envios_tracking_ids).issubset(envios_at_deposit):
                msg = (
                    "Some of the Envíos with ids %s don't exist or "
                    "are not at the deposit with id=%s."
                ) % (envios_tracking_ids, pk)
                raise serializers.ValidationError({"response": msg})

    def save(self):
        author = self.validated_data['created_by']
        from_deposit = self.validated_data['from_deposit']
        to_carrier = self.validated_data['to_carrier']
        envios_tracking_ids = self.validated_data['envios_tracking_ids']
        return withdraw_by_envios_tracking_ids(
            author, from_deposit, to_carrier, *envios_tracking_ids)


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
        if not set(towns_ids).issubset(towns_ids_on_deposit):
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


class EnviosToWithdrawFilteredRequestSerializer(serializers.ModelSerializer):

    envios_tracking_ids = serializers.ListField(
        child=serializers.CharField(), allow_empty=True, required=False)

    partidos_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True, required=False)

    towns_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True, required=False)

    class Meta:
        model = TrackingMovement
        fields = (
            'from_deposit',
            'envios_tracking_ids',
            'partidos_ids',
            'towns_ids',
        )
        extra_kwargs = {
            'from_deposit': {'required': True, },
            'envios_tracking_ids': {'required': False, },
            'partidos_ids': {'required': False, },
            'towns_ids': {'required': False, },
        }

    def parse_envio_data(self, envio) -> dict:
        address = envio.full_address
        partido = envio.town.partido
        client = envio.client.name
        return {
            'tracking_id': envio.tracking_id,
            'data': f"{address}, {partido} de {client}"
        }

    def save(self):
        filters = {
            'status__in': [Envio.STATUS_NEW, Envio.STATUS_STILL],
        }
        from_deposit = self.validated_data.get('from_deposit', None)
        if from_deposit is not None:
            filters['deposit__id'] = from_deposit.pk
        envios_tracking_ids = self.validated_data.get(
            'envios_tracking_ids', None)
        if envios_tracking_ids is not None:
            print("envios_tracking_ids", envios_tracking_ids)
            filters['tracking_id__in'] = envios_tracking_ids
        partidos_ids = self.validated_data.get('partidos_ids', None)
        if partidos_ids is not None:
            filters['town__partido__id__in'] = partidos_ids
        towns_ids = self.validated_data.get('towns_ids', None)
        if towns_ids is not None:
            filters['town__id__in'] = towns_ids
        envios = Envio.objects.filter(**filters).distinct()
        return {
            'envios': [self.parse_envio_data(envio) for envio in envios],
            'count': len(envios),
        }
