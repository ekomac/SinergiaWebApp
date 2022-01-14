from collections import Counter
from typing import Any, Callable, Dict, List, Tuple

from openpyxl import Workbook
from openpyxl.styles import PatternFill
from envios.models import BulkLoadEnvios, Envio
from tracking.models import TrackingMovement
from places.models import Partido, Town


ABBREVIATIONS = {
    "GRAL": "GENERAL",
    "GENERAL": "GRAL",
    "CNEL": "CORONEL",
    "CORONEL": "CNEL",
    "PTE": "PRESIDENTE",
    "PRESIDENTE": "PTE",
    "TTE": "TENIENTE",
    "TENIENTE": "TTE",
    "SGTO": "SARGENTO",
    "SARGENTO": "SGTO",
    "KM": "KILOMETRO",
    "KILOMETRO": "KM",
    "EST": "ESTACION",
    "ESTACION": "EST",
    "VICENTE": "VTE",
    "VTE": "VICENTE",
    "BS AS": "CABA",
    "BSAS": "CABA",
}


class NoSuggestionsAvailable(Exception):
    pass


def town_resolver(
        town: str, partido: str = None, zip_code: str = None) -> Town:
    resolver = TownSuggestionResolver(town, partido, zip_code)
    result, reason = resolver.resolve()
    if not result:
        raise NoSuggestionsAvailable("Nothing found")
    return (result, reason)
    #             la localidad con el nombre {cols[4]}


class TownSuggestionResolver:

    BASE_REASON_STR = "Se encontró al buscar la localidad "

    def __init__(self, town: str, partido: str = None, zip_code: str = None):
        self.town_name: str = town.upper()
        self.zip_code_num: str = zip_code.upper() if zip_code else None
        self.partido_name: str = partido.upper() if partido else None
        self.found_towns: List[Town] = []
        self.result: Town = None
        self.next_step: Callable = self.__query_town_name
        self.reason_of_match: str = None

    def resolve(self) -> Tuple[Town, str]:
        self.__main_loop()
        return (self.result, self.reason_of_match)

    def __main_loop(self):
        while self.next_step:
            towns, self.next_step = self.next_step()
            if towns is not None and len(towns) > 0:
                if len(towns) > 1:
                    self.found_towns.extend(towns)
                else:
                    self.result = towns[0]
                    self.next_step = None

    def __update_reason(self, reason):
        self.reason_of_match = self.BASE_REASON_STR + reason

    def __query_town_name(self) -> Tuple[List[Town], Callable]:
        self.__update_reason("con el nombre")
        towns = list(Town.objects.filter(name=self.town_name))
        return (towns, self.__query_town_name_and_partido)

    def __query_town_name_and_partido(self) -> Tuple[List[Town], Callable]:
        self.__update_reason("con las letras del nombre y el partido")
        towns = list(
            Town.objects.filter(name__contains=self.town_name,
                                partido__name=self.partido_name)
        )
        return (towns, self.__query_cleaned_town_name)

    def __query_cleaned_town_name(self) -> Tuple[List[Town], Callable]:
        self.__update_reason("con el nombre limpio, sin comas, puntos, etc.")
        self.town_name = self.town_name.replace(
            ".", "").replace("-", "").upper()
        towns = list(Town.objects.filter(name=self.town_name))
        return (towns, self.__query_town_part_of_name)

    def __query_town_part_of_name(self) -> Tuple[List[Town], Callable]:
        self.__update_reason(
            "con el nombre proporcionado como parte del nombre real.")
        towns = list(Town.objects.filter(name__contains=self.town_name))
        return (towns, self.__query_replacing_abbreviations)

    def __query_replacing_abbreviations(self) -> Tuple[List[Town], Callable]:
        self.__update_reason("con el nombre sin abreviaturas.")
        town = self.town_name
        for key, value in ABBREVIATIONS.items():
            if key in town:
                town.replace(key, value)
        towns = list(Town.objects.filter(name=town))
        return (towns, self.__query_postal_code)

    def __query_postal_code(self) -> Tuple[List[Town], Callable]:
        self.__update_reason("con el código postal.")
        towns = None
        if self.zip_code_num:
            towns = list(Town.objects.filter(zipcode__code=self.zip_code_num))
        return (towns, self.__query_most_matching_name)

    def __query_most_matching_name(self) -> Tuple[List[Town], Callable]:
        self.__update_reason("que tuvo más coincidencias.")
        town = self.town_name
        words = filter(lambda w: len(w) > 3, town.split(" "))
        towns = []
        for word in words:
            towns.extend(list(Town.objects.filter(name__contains=word)))
        if towns:
            counted = Counter(towns)
            ordered = counted.most_common()
            most_common = counted.most_common(1)[0][1]
            towns.clear()
            for item, score in ordered:
                if score == most_common:
                    towns.append(item)
                else:
                    break
        return (towns, self.__query_found_towns_most_matching_name)

    def __query_found_towns_most_matching_name(
            self
    ) -> Tuple[List[Town], Callable]:
        self.__update_reason("que tuvo más coincidencias.")
        if self.found_towns:
            counted = Counter(self.found_towns)
            ordered = counted.most_common()
            most_common = counted.most_common(1)[0][1]
            self.found_towns.clear()
            for item, score in ordered:
                if score == most_common:
                    self.found_towns.append(item)
                else:
                    break
        return (self.found_towns, self.__query_partido_as_name)

    def __query_partido_as_name(self) -> Tuple[List[Town], Callable]:
        self.__update_reason("con el partido como nombre.")
        towns = None
        if self.partido_name:
            query_name = self.partido_name.upper()
            towns = list(Town.objects.filter(name=query_name))
        return (towns, self.__query_partido_as_name_replacing_abbreviations)

    def __query_partido_as_name_replacing_abbreviations(
        self
    ) -> Tuple[List[Town], Callable]:
        self.__update_reason("con el partido como nombre sin abreviaturas.")
        towns = None
        if self.partido_name:
            query_name = self.partido_name.upper()
            for key, value in ABBREVIATIONS.items():
                if key in query_name:
                    query_name.replace(key, value)
            towns = list(Town.objects.filter(name=query_name))
        return (towns, self.__query_partido_as_part_of_name)

    def __query_partido_as_part_of_name(self) -> Tuple[List[Town], Callable]:
        self.__update_reason("con el partido como parte nombre.")
        towns = None
        if self.partido_name:
            query_name = self.partido_name.upper()
            towns = list(Town.objects.filter(name__contains=query_name))
        return (towns, self.__query_first_town_in_partido)

    def __query_first_town_in_partido(self):
        self.reason_of_match = "Es la primera localidad \
            del partido proporcionado"
        towns = []
        if self.partido_name:
            partidos = Partido.objects.filter(name=self.partido_name)
            if partidos:
                towns = partidos[0].town_set.all()
                if towns:
                    towns.order_by("name")
        return (towns, None)


def create_xlsx_workbook(
    csv_str: str, cells_to_paint: str = None
) -> Workbook:
    # Create an excel workbook
    wb = Workbook()
    # Get first sheet (1 is created when wb created)
    sheet = wb.active
    # Change title to 'Datos'
    sheet.title = 'Datos'
    # Get the sheet recently changed
    sheet = wb.get_sheet_by_name('Datos')
    # The default amount of columns
    COLUMNS = 10
    # Parse the csv string to list of lists
    result = [row.split(",") for row in csv_str.split("\n")]
    col_names = [
        "ID FLEX", "DOMICILIO", "ENTRECALLES", "CODIGO POSTAL",
        "LOCALIDAD", "PARTIDO", "DESTINATARIO", "DNI DESTINATARIO",
        "TELEFONO DESTINATARIO", "DETALLE DEL ENVIO"]
    result[0] = col_names
    # Iterate over rows and cols indexes
    for i in range(len(result)):
        for j in range(COLUMNS):

            # Get the cell at i and j
            cell = sheet.cell(row=i+1, column=j+1)

            # Set the value to the corresponding csv row and col
            if i != 0 and j == 4:
                try:
                    if result[i][j] and str(result[i][j]).isdigit():
                        cell.value = Town.objects.get(id=result[i][j]).name
                    else:
                        cell.value = ""
                except Town.DoesNotExist:
                    cell.value = ""
            else:
                cell.value = result[i][j]

            # Cell reference as pair values as string
            cell_ref = f"{i},{j}"

            # If the cell_ref is in csv_errors
            if cells_to_paint and cell_ref in cells_to_paint:
                # Change the bg color to yellow
                cell.fill = PatternFill("solid", fgColor="FFFF00")
    return wb


def bulk_create_envios(
    bulk_load_envios: BulkLoadEnvios
) -> List[Envio]:
    """
    Create envios from the csv file and return them.
    Ids are returned just because PostgreSQL supports it.
    """
    # Get the csv file
    envios = []
    for i, row in enumerate(bulk_load_envios.csv_result.split("\n")):
        if i == 0 or "traking_id" in row:
            continue
        cols = row.split(",")
        kwargs = __cols_to_kwargs(cols, bulk_load_envios)
        envio = Envio(**kwargs)
        # print("deposit", bulk_load_envios.deposit)
        envio.deposit = bulk_load_envios.deposit
        # print("envio.deposit", envio.deposit)
        envio.save()
        envios.append(envio)
    # envios = Envio.objects.bulk_create(envios)
    # for envio in envios:
    #     # For every envio, create a tracking movement
    #     base_create_tracking(envio)
    author = envios[0].updated_by
    tm = TrackingMovement(
        created_by=author,
        action=TrackingMovement.ACTION_ADDED_TO_SYSTEM,
        result=TrackingMovement.RESULT_ADDED_TO_SYSTEM,
        deposit=bulk_load_envios.deposit
    )
    tm.save()
    tm.envios.add(*envios)
    return envios


def __cols_to_kwargs(
    cols: List[str], bulk_load_envios: BulkLoadEnvios
) -> Dict[str, Any]:
    kwargs = {
        'street': cols[1],
        'remarks': cols[2],
        'zipcode': cols[3],
        'town': Town.objects.get(pk=cols[4]),
        'name': cols[6],
        'doc': cols[7],
        'phone': cols[8],
        'detail': cols[9] if cols[9] else "0-1",
        'updated_by': bulk_load_envios.created_by,
        'client': bulk_load_envios.client,
        # 'state_ptr__deposit': bulk_load_envios.deposit,
        'bulk_upload_id': bulk_load_envios.pk,
    }
    if cols[0]:
        kwargs['is_flex'] = True
        kwargs['flex_id'] = cols[0]
    return kwargs
