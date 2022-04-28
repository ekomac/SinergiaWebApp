from django.core.files.uploadedfile import InMemoryUploadedFile
from envios.utils import NoSuggestionsAvailable, town_resolver

from places.models import Town
from .exceptions import UnsupportedExtensionError
from .pdf_module import PDFModule
from .excel_module import ExcelModule
from .shipment import Shipment
from typing import Any, Dict, List


class AddressNotFound(Exception):
    pass


class TownNotFound(Exception):
    pass


class Extractor:

    def __init__(self):
        self.file = None
        self.file_name = None
        self.errors = []
        self.needs_manual_fix = False
        self.cells_to_paint = []

    def get_shipments(
            self, in_mem_file: InMemoryUploadedFile
    ) -> Dict[str, Any]:
        self.file = in_mem_file
        self.file_name = self.file.name
        shipments = self.__do_extraction()
        return {
            'result': self.__shipments_to_csv(shipments),
            'count': len(shipments),
            'errors': "\n".join(self.errors),
            'needs_manual_fix': self.needs_manual_fix,
            'cells_to_paint': "-".join(self.cells_to_paint),
        }

    def __do_extraction(self) -> List[Shipment]:
        self.module = None
        if self.file_name.lower().endswith(('.pdf')):
            self.module = PDFModule(self.file)
        elif self.file_name.lower().endswith(('.xlsx')):
            self.module = ExcelModule(self.file)
        else:
            last_stop_index = self.file_name.rindex(".")
            extension = self.file_name[last_stop_index+1:]
            raise UnsupportedExtensionError(
                f"The extension {extension} is not supported yet")
        return self.module.extract_shipments()

    def __shipments_to_csv(self, shipments: list) -> str:
        titles = "traking_id,domicilio,referencia," + \
            "codigo_postal,localidad,partido,destinatario," + \
            "dni_destinatario,telefono,detalle_envio,cargos_destinatario"
        shipments_mapped = [self.__shipment_as_csv_row_string(
            i, shipment) for i, shipment in enumerate(shipments)]
        shipments_str = "\n".join(shipments_mapped)
        return f'{titles}\n{shipments_str}'

    def __shipment_as_csv_row_string(
        self,
        index: int,
        shipment: Shipment
    ) -> str:
        if not shipment.domicilio:
            self.cells_to_paint.append(f"{index+1},1")
            self.errors.append(
                f"En la fila {index+1}, columna 2, no " +
                "se proporcionó un domicilio")
            self.needs_manual_fix = True
        if not shipment.codigo_postal and not shipment.localidad \
                and not shipment.partido:
            self.cells_to_paint.append(f"{index+1},3")
            self.cells_to_paint.append(f"{index+1},4")
            self.cells_to_paint.append(f"{index+1},5")
            self.errors.append(
                f"En la fila {index+1}, no se proporcionaron suficientes \
                    datos para encontrar la localidad.")
            self.needs_manual_fix = True
            town = ""
        else:
            town = self.__resolve_town(
                index, shipment.localidad,
                shipment.partido, shipment.codigo_postal)
        values = [
            shipment.tracking_id, shipment.domicilio, shipment.referencia,
            shipment.codigo_postal, town, shipment.partido,
            shipment.destinatario, shipment.dni_destinatario,
            shipment.phone, shipment.detalle_envio, shipment.cargos
        ]
        return ",".join(map(str, values))

    def __resolve_town(self, index, town_name, partido, postal_code):
        towns = Town.objects.filter(name=town_name.upper())
        if not towns or len(towns) > 1:
            self.cells_to_paint.append(f"{index+1},4")
            try:
                self.cells_to_paint.append(f"{index+1},4")
                result, reason = town_resolver(town_name, partido, postal_code)
                self.errors.append(
                    f'En la fila {index+1}, columna 5, no se encontró ' +
                    f'la localidad con el nombre {town_name}. ¿Acaso ' +
                    f'quisiste decir {result}? {reason}')
                return result.id
            except NoSuggestionsAvailable:
                if not town_name:
                    self.errors.append(
                        f"En la fila {index+1}, columna 5, no se " +
                        'proporcionó una localidad')
                else:
                    self.errors.append(
                        f'En la fila {index+1}, columna 5, no se encontró ' +
                        f'la localidad con el nombre {town_name} ' +
                        ', y no tenemos sugerencias para vos.')
                self.needs_manual_fix = True
                return ""
        return towns[0].id
