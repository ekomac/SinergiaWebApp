from rest_framework import serializers

from envios.models import Envio
from places.models import Partido, Town
from tracking.models import TrackingMovement
from tracking.utils.devolver import (
    devolver_all,
    devolver_by_envios_tracking_ids,
    devolver_by_partidos_ids,
    devolver_by_towns_ids,
)


class BaseDevolverSerializer(serializers.ModelSerializer):

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


class DevolverAllSerializer(BaseDevolverSerializer):
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
        return devolver_all(author, from_carrier, to_deposit)


class DevolverByEnviosTrackingIdsSerializer(BaseDevolverSerializer):

    envios_tracking_ids = serializers.ListField(
        child=serializers.CharField(max_length=50),
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
        envios_tracking_ids = data['envios_tracking_ids']
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
        return devolver_by_envios_tracking_ids(
            author, from_carrier, to_deposit, *envios_tracking_ids)


class DevolverByTownsIdsSerializer(BaseDevolverSerializer):
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
        return devolver_by_towns_ids(
            author, from_carrier, to_deposit, *towns_ids)


class DevolverByPartidosIdsSerializer(BaseDevolverSerializer):

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
        return devolver_by_partidos_ids(
            author, from_carrier, to_deposit, *partidos_ids)


class EnviosToDevolverFilteredRequestSerializer(serializers.ModelSerializer):

    envios_tracking_ids = serializers.ListField(
        child=serializers.CharField(), allow_empty=True, required=False)

    partidos_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True, required=False)

    towns_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True, required=False)

    class Meta:
        model = TrackingMovement
        fields = (
            'from_carrier',
            'envios_tracking_ids',
            'partidos_ids',
            'towns_ids',
        )
        extra_kwargs = {
            'from_carrier': {'required': True, },
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
            'status__in': [Envio.STATUS_MOVING],
        }
        from_carrier = self.validated_data.get('from_carrier', None)
        if from_carrier is not None:
            filters['carrier__id'] = from_carrier.pk
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
