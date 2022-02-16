# REST FRAMEWORK
from rest_framework import serializers

# PROJECT
from account.models import Account


class EmployeeSerializer(serializers.ModelSerializer):

    envios = serializers.SerializerMethodField('get_envios_from_account')
    full_name = serializers.SerializerMethodField('get_full_name_from_account')
    profile_picture_url = serializers.SerializerMethodField(
        'get_profile_picture_url_from_account')
    permission = serializers.SerializerMethodField(
        'get_permission_from_account')

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
            'permission',
        )

    def get_envios_from_account(self, account):
        return account.envios_carried_by.count()

    def get_full_name_from_account(self, account):
        return account.full_name

    def get_profile_picture_url_from_account(self, account):
        return account.profile_picture.url if account.profile_picture else None

    def get_permission_from_account(self, account: Account):
        if account.groups.exists():
            return account.groups.first().name
        return None
