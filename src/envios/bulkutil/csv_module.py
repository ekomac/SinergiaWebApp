from .base_module import ShipmentExractorModule


class CSVModule(ShipmentExractorModule):
    def __init__(self, filepath, **kwargs):
        super().__init__(filepath, **kwargs)

    def extract_shipments(self):
        raise NotImplementedError("The writing down of this is in progress.")
