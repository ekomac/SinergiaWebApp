# REST FRAMEWORK
from rest_framework import serializers

# PROJECT
from account.models import Account


class EmployeeSerializer(serializers.ModelSerializer):

    envios = serializers.SerializerMethodField('get_envios_from_account')
    full_name = serializers.SerializerMethodField('get_full_name_from_account')
    profile_picture_url = serializers.SerializerMethodField(
        'get_profile_picture_url_from_account')

    class Meta:
        model = Account
        fields = (
            'pk',
            'email',
            'username',
            'full_name',
            'first_name',
            'last_name',
            'profile_picture_url',
            'envios',
        )

    def get_envios_from_account(self, account):
        return account.Carrier.count()

    def get_full_name_from_account(self, account):
        return account.full_name

    def get_profile_picture_url_from_account(self, account):
        return account.profile_picture.url if account.profile_picture else None
