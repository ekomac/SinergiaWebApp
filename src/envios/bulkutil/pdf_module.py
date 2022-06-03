import re
from django.core.files.uploadedfile import InMemoryUploadedFile
import fitz
from itertools import chain
from .base_module import ShipmentExractorModule
from .exceptions import EmptyPDFError, InvalidPdfFileError
from .shipment import Shipment


class MercadoLibreSubmodule():

    def __init__(self, pdf, **kwargs):
        self.pdf = pdf
        self.shipments = []

    def extract_shipments(self):
        # Filter last pages containing summary table
        pages = filter(
            lambda page: 'Despacha tu producto' not in page.getText(),
            self.pdf)
        # Map each page to a list o shipments
        list_of_shipments_lists = map(self.__page_to_shipments, pages)
        # Flatten the list containing list of shipments
        return list(chain(*list_of_shipments_lists))

    def __page_to_shipments(self, page):
        page_text = page.getText()
        if "Barrio" in page_text:
            regex = re.compile(r'(\nBarrio:[\sA-Za-z0-9]{0,}\n)')
        else:
            regex = re.compile(r'(\nCP:[\s0-9]{4,}\n)')
        page_text = regex.sub(r'\1<<<COLUMN-END>>>\n', page_text)
        parts = page_text.split('<<<COLUMN-END>>>\n')
        return map(self.__part_to_shipment, parts[:-1])

    def __part_to_shipment(self, part) -> Shipment:
        lines = part.split("\n")
        if lines[0] == "":
            return None

        # Get tracking id
        regex = re.compile(r'\nTracking:(?P<result>.*)\n')
        tracking_id = regex.search(part).group("result").strip()

        # Get address
        regex = re.compile(r'\nDireccion:(?P<result>.*)\n')
        domicilio = regex.search(part).group("result").strip()

        # Get reference
        regex = re.compile(r'\s+Referencia:(?P<result>(.|\n)*)CP')
        referencia = regex.search(part).group("result").strip()
        referencia = " ".join(referencia.split("\n")).strip()

        # Get postal code
        regex = re.compile(r'\nCP:(?P<result>.*)\n')
        codigo_postal = regex.search(part).group("result").strip()

        # Get town and partido
        regex = re.compile(
            r'\n(?P<part>.*)\n(?P<loc>.*)\nDestinatario')
        partido = regex.search(part).group("part").strip()
        town = regex.search(part).group("loc").strip()

        # Get receiver name
        regex = re.compile(r'(\nDestinatario:(?P<result>.*)\n)')
        destinatario = regex.search(part).group("result").strip()

        # Set receiver phone
        phone = ""
        # Set default details
        detalle_envio = "0-1"

        # Return the shipment with the declared properties
        shipment = Shipment(tracking_id, domicilio, referencia,
                            codigo_postal, town, partido,
                            destinatario, "", phone, detalle_envio)
        shipment.clean()
        return shipment


class TiendaNubeSubmodule():

    def __init__(self, pdf, **kwargs):
        self.pdf = pdf
        self.shipments = []

    def extract_shipments(self):
        # Map each page to a list o shipments
        list_of_shipments_lists = map(self.__page_to_shipments, self.pdf)
        return list(chain(*list_of_shipments_lists))

    def __page_to_shipments(self, page):
        page_text = page.getText()
        text = page_text.replace("\n", "<<<")
        try:
            parts = re.findall(r'Enviar a:<<<(.+?)Producto', text)
            return map(self.__part_to_shipment, parts)
        except AttributeError:
            raise EmptyPDFError("The PDF provided has no shipments in it.")

    def __part_to_shipment(self, part):
        # Get destination's info
        destination = re.findall(r'<<<(.*),<<<Argentina', part)[0]
        destination_parts = destination.split("<<<")

        # Define the Shipment2's properties
        traking_id = ""
        domicilio = ""
        codigo_postal = destination_parts[-1].split(",")[-1].strip()
        localidad = ""
        partido = destination_parts[-1].split(",")[-3].strip()
        destinatario = re.search(r'(.*?)<<<', part).group(1)
        detalle_envio = "0-1"
        referencias = re.findall(r'Notas del cliente:<<<(.*)<<<', part)
        referencia = "".join(referencias)
        phones = re.findall(r'Teléfono: \+(\d*)', part)
        phone = "".join(phones)

        try:
            localidad = destination_parts[-1].split(",")[-4].strip()
            domicilio = " ".join(destination_parts[:-1]).strip()
        except IndexError:
            if len(destination_parts) == 2:
                localidad = partido
                domicilio = destination_parts[0].strip()
            else:
                localidad = destination_parts[-2].strip()
                domicilio = "".join(
                    destination_parts[:-2]).replace("<<<", " ").strip()

        # Return the shipment with the declared properties
        shipment = Shipment(traking_id, domicilio, referencia,
                            codigo_postal, localidad, partido,
                            destinatario, "", phone, detalle_envio)
        shipment.clean()
        return shipment


class PDFModule(ShipmentExractorModule):

    def __init__(self, file: InMemoryUploadedFile, **kwargs):
        super(PDFModule, self).__init__(file, **kwargs)

    def extract_shipments(self):
        file: InMemoryUploadedFile = self.file
        with fitz.open(None, file.read(), 'pdf') as pdf:
            first_page = pdf[0]
            fp_text = first_page.getText()
            submodule = None
            if self.__is_mercado_libre(fp_text):
                submodule = MercadoLibreSubmodule(pdf)
            elif self.__is_tienda_nube(fp_text):
                submodule = TiendaNubeSubmodule(pdf)
            else:
                raise InvalidPdfFileError(
                    "El pdf proporcionado no es de" +
                    " Mercado Libre ni de TiendaNube")
            return submodule.extract_shipments()

    def __is_mercado_libre(self, text):
        return 'Mercado Envíos' in text \
            or 'Flex' in text or 'Recorta' in text

    def __is_tienda_nube(self, text):
        regex = re.compile(r'Orden: #\d+')
        result = regex.findall(text)
        return len(result) > 0
