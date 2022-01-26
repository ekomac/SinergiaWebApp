from account.models import Account
from envios.models import Envio


def send_back_to_original_deposit(modeladmin, request, queryset):
    for envio in queryset:
        deposit = envio.client.deposit_set.first()
        envio.deposit = deposit
        envio.carrier = None
        envio.status = Envio.STATUS_NEW
        envio.save()


def withdraw_by_superuser(modeladmin, request, queryset):
    for envio in queryset:
        envio.deposit = None
        envio.carrier = Account.objects.filter(is_superuser=True).first()
        envio.status = Envio.STATUS_MOVING
        envio.save()


actions = [
    send_back_to_original_deposit,
    withdraw_by_superuser
]
