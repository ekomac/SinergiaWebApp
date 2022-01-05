import json
from places.models import Town


def get_localidades_as_JSON():
    query = Town.objects.all().order_by('name')
    mapped = list(map(map_town_to_dict, query))
    return json.dumps(mapped)


def map_town_to_dict(town):
    return {
        'id': town.id,
        'name': town.name.title(),
        'partido_id': town.partido.id,
    }
