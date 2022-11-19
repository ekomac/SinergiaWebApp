from openpyxl.worksheet.table import Table, TableStyleInfo
from django.db.models.functions import Cast
from django.db.models import FloatField
import json
from typing import Dict, List, Tuple
from openpyxl import Workbook
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
    return result


def cast_towns_to_lists() -> List[Tuple]:
    """
    Returns towns as tupes with the following values:
    00. partido.province
    01. partido.name
    02. name
    03. flex_code.code
    04. flex_code.price
    05. delivey_code.code
    06. delivery_code.max_5k_price
    07. delivery_code.bulto_max_10k_price
    08. delivery_code.bulto_max_20k_price
    09. delivery_code.miniflete_price
    10. delivery_code.tramite_price
    11. delivery_code.camioneta_price
    """
    return list(Town.objects.all().order_by(
        "partido__province", "partido__name", "name"
    ).annotate(
        flex_price=Cast('flex_code__price', FloatField()),
        max_5k_price=Cast("delivery_code__max_5k_price", FloatField()),
        bulto_max_10k_price=Cast(
            "delivery_code__bulto_max_10k_price", FloatField()),
        bulto_max_20k_price=Cast(
            "delivery_code__bulto_max_20k_price", FloatField()),
        miniflete_price=Cast("delivery_code__miniflete_price", FloatField()),
        tramite_price=Cast("delivery_code__tramite_price", FloatField()),
        camioneta_price=Cast("delivery_code__camioneta_price", FloatField()),
    ).values_list(
        "partido__province",
        "partido__name",
        "name",
        "flex_code__code",
        "flex_price",
        "delivery_code__code",
        "max_5k_price",
        "bulto_max_10k_price",
        "bulto_max_20k_price",
        "miniflete_price",
        "tramite_price",
        "camioneta_price",
    ))


def create_places_and_prices_xlsx_workbook() -> Workbook:
    wb = Workbook()
    sheet = wb.active
    sheet.title = 'Datos'
    sheet = wb.get_sheet_by_name('Datos')

    col_names = [
        ("Provincia", "Partido", "Nombre", "Zona Mercado Envíos Flex",
         "Precio Mercado Envíos Flex", "Zona", "Paquete <= 5kg",
         "Bulto <= 10kg", "Bulto <= 20kg", "Miniflete", "Trámite",
         "Camioneta")
    ]
    towns = cast_towns_to_lists()
    data = col_names + towns
    for row in data:
        sheet.append(row)

    table = Table(ref=f'A1:L{len(data)}',
                  displayName='Localidades')

    mediumStyle = TableStyleInfo(name='TableStyleMedium2',
                                 showRowStripes=True)
    table.tableStyleInfo = mediumStyle

    sheet.add_table(table)

    return wb
