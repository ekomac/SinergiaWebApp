import json
from clients.models import Client


def get_clients_as_JSON():
    query = Client.objects.all().order_by('name')
    mapped = list(map(map_client_to_dict, query))
    return json.dumps(mapped)


def map_client_to_dict(client):
    return {
        'id': client.id,
        'name': client.name,
    }
