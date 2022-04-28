import unidecode
from dataclasses import dataclass


@dataclass
class Shipment:
    tracking_id: str = ""
    domicilio: str = ""
    referencia: str = ""
    codigo_postal: str = ""
    localidad: str = ""
    partido: str = ""
    destinatario: str = ""
    dni_destinatario: str = ""
    phone: str = ""
    detalle_envio: str = ""
    cargos: str = "0"

    def clean(self):
        self.replace_commas()
        self.replace_accents()
        return

    def replace_commas(self):
        self.tracking_id = str(self.tracking_id).replace(
            ",", " ").replace("  ", " ")
        self.domicilio = str(self.domicilio).replace(
            ",", " ").replace("  ", " ")
        self.referencia = str(self.referencia).replace(
            ",", " ").replace("  ", " ")
        self.codigo_postal = str(self.codigo_postal).replace(
            ",", " ").replace("  ", " ")
        self.localidad = str(self.localidad).replace(
            ",", " ").replace("  ", " ")
        self.partido = str(self.partido).replace(",", " ").replace("  ", " ")
        self.destinatario = str(self.destinatario).replace(
            ",", " ").replace("  ", " ")
        self.dni_destinatario = str(self.dni_destinatario).replace(
            ",", " ").replace("  ", " ")
        self.phone = str(self.phone).replace(",", " ").replace("  ", " ")
        self.detalle_envio = str(self.detalle_envio).replace(
            ",", " ").replace("  ", " ")
        if "." in str(self.cargos):
            dot = str(self.cargos).index(".")
            self.cargos = str(self.cargos).strip()[:dot]
        if "," in str(self.cargos):
            comma = str(self.cargos).index(",")
            self.cargos = str(self.cargos).strip()[:comma]
        return

    def replace_accents(self):
        self.tracking_id = unidecode.unidecode(self.tracking_id)
        self.domicilio = unidecode.unidecode(self.domicilio)
        self.referencia = unidecode.unidecode(self.referencia)
        self.codigo_postal = unidecode.unidecode(self.codigo_postal)
        self.localidad = unidecode.unidecode(self.localidad)
        self.partido = unidecode.unidecode(self.partido)
        self.destinatario = unidecode.unidecode(self.destinatario)
        self.dni_destinatario = unidecode.unidecode(self.dni_destinatario)
        self.phone = unidecode.unidecode(self.phone)
        self.detalle_envio = unidecode.unidecode(self.detalle_envio)
        self.cargos = unidecode.unidecode(self.cargos)
        return

    def is_not_empty(self):
        return len(self.tracking_id) > 0 or len(self.domicilio) > 0 \
            or len(self.referencia) > 0 \
            or len(self.codigo_postal) > 0 \
            or len(self.localidad) > 0 \
            or len(self.partido) > 0 \
            or len(self.destinatario) > 0 \
            or len(self.dni_destinatario) > 0 \
            or len(self.phone) > 0 \
            or len(self.detalle_envio) > 0 \
            or len(self.cargos) > 0
