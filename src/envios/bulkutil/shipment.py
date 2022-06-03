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
        for attr in self.__dict__:
            if isinstance(self.__dict__[attr], str):
                self.__dict__[attr] = unidecode.unidecode(
                    self.__dict__[attr])
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
