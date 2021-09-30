from rest_framework import serializers
from places.models import Town


class TownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Town
        fields = ['name', 'partido', 'delivery_code', 'flex_code']
