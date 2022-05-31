import json
from typing import Dict, List
from places.models import Partido, Town
from prices.models import DeliveryCode


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


def get_places_data_for_dcode(dcode: DeliveryCode) -> Dict[str, List[str]]:
    result = {
        'id': dcode.id,
        'code': dcode.code,
        'max_5k_price': dcode.max_5k_price,
        'bulto_max_10k_price': dcode.bulto_max_10k_price,
        'bulto_max_20k_price': dcode.bulto_max_20k_price,
        'miniflete_price': dcode.miniflete_price,
        'tramite_price': dcode.tramite_price,
        "partidos": [],
        "towns": []
    }
    for partido in Partido.objects.filter(
            town__delivery_code__in=[dcode]).distinct():
        print("Partido", partido.name)
        towns = Town.objects.filter(partido=partido)
        total_towns = len(towns)
        print("total towns:", total_towns)
        try:
            if (total_towns > 0):
                first_code = towns[0].delivery_code.code
                with_same_code = list(filter(
                    lambda x: x.delivery_code.code == first_code, towns))
                print("with same code:", len(with_same_code))
                if total_towns == len(with_same_code):
                    result["partidos"].append(partido.name)
                else:
                    raise AttributeError("")
        except AttributeError:
            for town in towns:
                result["towns"].append(town.name)
    print()
    print()
    print()
    return result
