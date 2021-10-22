from django.core.files.uploadedfile import InMemoryUploadedFile
from .exceptions import (
    CantConvertNothing,
    FileWithNoExtension,
    InvalidExtension
)
from .pdf_module import PDFModule
from .excel_module import ExcelModule
from .csv_module import CSVModule
from .shipment import Shipment
from typing import Tuple


class Extractor():

    def __init__(
            self, in_mem_file: InMemoryUploadedFile = None, ** kwargs):
        self.file = in_mem_file
        self.file_name = self.file.name if self.file else None

    def get_shipments(
            self, in_mem_file: InMemoryUploadedFile = None) -> Tuple[str, int]:
        """Initializes convertion of file to csv

        Args:
            in_mem_file (django.core.files.uploadedfile.InMemoryUploadedFile,
             optional): loaded in memory, post from django view.
             Defaults to None.

        Raises:
            TypeError: if given filepath isn't a string.
            CantConvertNothing: if there wasn't any filepath
            provided (if it's none).
            FileWithNoExtension: if the file doesn't have an extension.

        Returns:
            Tuple[str, int]: csv string containing shipments's data
            and shipments count as int
        """
        # If in_mem_file was provided here, update self.in_mem_file
        if in_mem_file:
            self.file = in_mem_file
            self.file_name = self.file.name

        # If no in_mem_file was provided
        if not self.file:
            raise CantConvertNothing("No file was provided.")

        try:
            if self.file_name:
                # Find last '.' (stop)
                last_stop = self.file_name.rindex(".")
                # Get the extension
                extension = self.file_name[last_stop+1:]
                # Extract the shipments
                shipments = self.__do_extraction(extension)
                # Return the shipments parsed as a csv
                return (self.__shipments_to_csv(shipments), len(shipments))

        except ValueError as e:
            print(e)
            # The file doesn't have an extension.
            raise FileWithNoExtension("File didn't contain an extension.")

    def __do_extraction(self, extension: str) -> list:
        """Extract the shipments from the file provided,
        for the specific given extension (pdf, xlsx, csv).

        Args:
            extension (str): a file extension expressed as a string.
            Compatible are: pdf, xlsx and csv. Pdf must be a file containing
            shipment labels from MercadoLibre and TiendaNube.

        Raises:
            InvalidExtension: for incompatible extensions
            (anything but pdf, xlsx & csv)

        Returns:
            list[Shipment2]: all the shipments found.
        """
        extraction_dict = {
            'pdf': PDFModule,
            'xlsx': ExcelModule,
            'csv': CSVModule,
        }
        try:
            module = extraction_dict[extension]
            return module(self.file).extract_shipments()
        except KeyError:
            raise InvalidExtension("Unknown file extension.")

    def __shipments_to_csv(self, shipments: list) -> str:
        """Parses all shipments to a csv string and adds the headers.

        Args:
            shipments (list[Shipment]): the shipments to parse.

        Returns:
            str: the csv string
        """
        titles = "traking_id,domicilio,referencia," + \
            "codigo_postal,localidad,partido,destinatario," + \
            "dni_destinatario,telefono,detalle_envio"
        shipments_mapped = list(map(
            self.__shipment_as_csv_row_string, shipments))
        shipments_str = "\n".join(shipments_mapped)
        return f'{titles}\n{shipments_str}'

    def __shipment_as_csv_row_string(self, shipment: Shipment) -> str:
        """Parses a Shipment object into a str as in a csv file's row.

        Args:
            shipment (Shipment): the object to map to string.

        Returns:
            str: the corresponding csv file's row.
        """
        values = [
            shipment.tracking_id, shipment.domicilio, shipment.referencia,
            shipment.codigo_postal, shipment.localidad, shipment.partido,
            shipment.destinatario, shipment.dni_destinatario,
            shipment.phone, shipment.detalle_envio,
        ]
        return ",".join(map(str, values))
