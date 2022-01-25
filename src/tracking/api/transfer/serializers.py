from rest_framework import serializers

from envios.models import Envio
from places.models import Partido, Town
from tracking.models import TrackingMovement
from tracking.utils.transfer import (
    transfer_all,
    transfer_by_envios_ids,
    transfer_by_partidos_ids,
    transfer_by_towns_ids,
    transfer_by_zones_ids
)


class BaseTransferSerializer(serializers.ModelSerializer):
    def check_carrier_is_carrier(self, carrier):
        if carrier.envios_carried_by.filter(
                status=Envio.STATUS_MOVING).count() == 0:
            raise serializers.ValidationError(
                {"response": "Carrier isn't carrying any Envíos."}
            )


class TransferAllSerializer(BaseTransferSerializer):
    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_carrier', 'to_carrier',)
        extra_kwargs = {
            'from_carrier': {'required': True, },
            'to_carrier': {'required': True, },
        }

    def save(self):
        author = self.validated_data['created_by']
        from_carrier = self.validated_data['from_carrier']
        to_carrier = self.validated_data['to_carrier']
        self.check_carrier_is_carrier(from_carrier)
        return transfer_all(author, from_carrier, to_carrier)


class TransferByEnviosIdsSerializer(BaseTransferSerializer):

    envios_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_carrier', 'to_carrier', 'envios_ids',)
        extra_kwargs = {
            'from_carrier': {'required': True, },
            'to_carrier': {'required': True, },
            'envios_ids': {'required': True, },
        }

    def save(self):
        author = self.validated_data['created_by']
        from_carrier = self.validated_data['from_carrier']
        to_carrier = self.validated_data['to_carrier']
        self.check_carrier_is_carrier(from_carrier)
        envios_ids = self.validated_data['envios_ids']

        if from_carrier.envios_carried_by.filter(
                pk__in=envios_ids).count() != len(envios_ids):
            raise serializers.ValidationError(
                {"response": "Some of the Envíos with given ids " +
                    "{} don't exist or aren't carried by {}.".format(
                        envios_ids, from_carrier.full_name)
                 }
            )
        return transfer_by_envios_ids(
            author, from_carrier, to_carrier, *envios_ids)


class TransferByTownsIdsSerializer(BaseTransferSerializer):

    towns_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_carrier', 'to_carrier', 'towns_ids',)
        extra_kwargs = {
            'from_carrier': {'required': True, },
            'to_carrier': {'required': True, },
            'towns_ids': {'required': True, },
        }

    def save(self):
        author = self.validated_data['created_by']
        from_carrier = self.validated_data['from_carrier']
        to_carrier = self.validated_data['to_carrier']
        self.check_carrier_is_carrier(from_carrier)
        towns_ids = self.validated_data['towns_ids']

        if from_carrier.envios_carried_by.filter(
                town__id__in=towns_ids).count() != len(
                    Town.objects.filter(pk__in=towns_ids)):
            raise serializers.ValidationError(
                {"response": "Some of the Towns with given ids {} ".format(
                    towns_ids
                ) + "don't correspond to Envíos carried by {}.".format(
                    from_carrier.full_name)
                }
            )
        return transfer_by_towns_ids(
            author, from_carrier, to_carrier, *towns_ids)


class TransferByPartidosIdsSerializer(BaseTransferSerializer):

    partidos_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_carrier', 'to_carrier', 'partidos_ids',)
        extra_kwargs = {
            'from_carrier': {'required': True, },
            'to_carrier': {'required': True, },
            'partidos_ids': {'required': True, },
        }

    def save(self):
        author = self.validated_data['created_by']
        from_carrier = self.validated_data['from_carrier']
        to_carrier = self.validated_data['to_carrier']
        self.check_carrier_is_carrier(from_carrier)
        partidos_ids = self.validated_data['partidos_ids']

        if from_carrier.envios_carried_by.filter(
                town__partido__id__in=partidos_ids
        ).count() != len(Partido.objects.filter(pk__in=partidos_ids)):
            raise serializers.ValidationError(
                {"response": "Some of the Partidos with given ids" +
                 " {} don't correspond to Towns ".format(partidos_ids) +
                 "of Envíos carried by {} (pk={}).".format(
                     from_carrier.full_name, from_carrier.pk)
                 }
            )
        return transfer_by_partidos_ids(
            author, from_carrier, to_carrier, *partidos_ids)


class TransferByZonesIdsSerializer(BaseTransferSerializer):

    zones_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        write_only=True, allow_empty=False)

    class Meta:
        model = TrackingMovement
        fields = ('created_by', 'from_carrier', 'to_carrier', 'zones_ids',)
        extra_kwargs = {
            'from_carrier': {'required': True, },
            'to_carrier': {'required': True, },
            'zones_ids': {'required': True, },
        }

    def save(self):
        author = self.validated_data['created_by']
        from_carrier = self.validated_data['from_carrier']
        to_carrier = self.validated_data['to_carrier']
        self.check_carrier_is_carrier(from_carrier)
        zones_ids = self.validated_data['zones_ids']

        if from_carrier.envios_carried_by.filter(
                town__partido__zone__id__in=zones_ids
        ).count() != len(zones_ids):
            raise serializers.ValidationError(
                {"response": "Some of the Zones with given ids" +
                 " {} don't correspond to Partidos of Towns ".format(
                     zones_ids
                 ) + "of Envíos carried by {}.".format(
                     from_carrier.full_name
                 )
                 }
            )
        return transfer_by_zones_ids(
            author, from_carrier, to_carrier, *zones_ids)
