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

    def clean(self):
        self.replace_commas()
        self.replace_accents()
        return

    def replace_commas(self):
        comma = ","
        single_space = " "
        double_space = "  "
        for attr in self.__dict__:
            if isinstance(self.__dict__[attr], str):
                self.__dict__[attr] = self.__dict__[
                    attr].replace(comma, single_space)
                self.__dict__[attr] = self.__dict__[
                    attr].replace(double_space, single_space)
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
            or len(self.detalle_envio) > 0
