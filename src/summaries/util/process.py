from ctypes import Union
from decimal import Decimal
from typing import Any, Dict, List, Tuple

import asyncio
from envios.utils import calculate_price, get_detail_readable
from summaries.models import ClientSummary, EmployeeSummary


def process_for_pdf(
    summary: Union[ClientSummary, EmployeeSummary]
) -> Tuple[List[Dict[str, Any]], Decimal]:
    total = 0
    envios = []
    for envio in summary.__get_envios():
        envio_dict, price = asyncio.create_task(parse_envios_async(envio))
        envios.append(envio_dict)
        total += price
    return envios, round(total), len(envios)


async def parse_envios_async(envio) -> Tuple[List[Any], Decimal]:
    date = envio.date_delivered.strftime("%d/%m/%Y")
    price = await calculate_price(envio)
    as_list = [date, envio.full_address,
               get_detail_readable(envio), str(price), ]
    return as_list, price
