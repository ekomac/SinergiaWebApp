from rest_framework import serializers
from places.models import Partido, Town, Zone


class TownSerializer(serializers.ModelSerializer):

    partido = serializers.SerializerMethodField('get_partido_from_town')

    class Meta:
        model = Town
        fields = ['pk', 'name', 'partido', 'delivery_code', 'flex_code']

    def get_partido_from_town(self, town):
        if town.partido:
            return {
                'pk': town.partido.pk,
                'name': town.partido.name.title(),
                'zone': {
                    'pk': town.partido.zone.pk,
                    'name': town.partido.zone.name.title(),
                }
            }
        return None


class PartidoSerializer(serializers.ModelSerializer):

    zone = serializers.SerializerMethodField('get_zone_from_partido')

    class Meta:
        model = Partido
        fields = ['pk', 'name', 'zone']

    def get_zone_from_partido(self, partido):
        if partido.zone:
            return {
                'pk': partido.zone.pk,
                'name': partido.zone.name.title(),
            }
        return None


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['pk', 'name', 'partido', 'delivery_code', 'flex_code']
