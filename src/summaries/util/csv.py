import csv
from typing import List

from django.http import HttpResponse
from envios.models import Envio
from summaries.models import Summary


class CSVSummary:

    def __init__(self, summary_id: int, repsonse: HttpResponse) -> None:
        self.summary = Summary.objects.get(id=summary_id)
        self.writer = csv.writer(repsonse)

    def get_csv_data(self) -> List[List[str]]:
        pass
