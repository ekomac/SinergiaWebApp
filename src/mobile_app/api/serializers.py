from rest_framework import serializers
from mobile_app.models import MobileApp


class MobileAppSerializer(serializers.ModelSerializer):

    class Meta:
        model = MobileApp
        fields = (
            'pk',
            'latest_version',
            'url',
            'created_at',
            'updated_at',
        )
