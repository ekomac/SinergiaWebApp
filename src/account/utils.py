import json
from account.models import Account


def get_employees_as_JSON():
    query = Account.objects.filter(
        client__isnull=True).exclude(role__in=['client']).order_by('last_name')
    mapped = list(map(map_account_to_dict, query))
    return json.dumps(mapped)


def map_account_to_dict(account):
    return {
        'id': account.id,
        'name': account.full_name_formal,
    }
