from ctypes import Union
from decimal import Decimal
from typing import Any, Dict, List, Tuple

import asyncio
from envios.utils import calculate_price
from summaries.models import ClientSummary, EmployeeSummary


def process_for_pdf(
    summary: Union[ClientSummary, EmployeeSummary]
) -> Tuple[List[Dict[str, Any]], Decimal]:
    total = 0
    envios = []
    for envio in summary.__get_envios():
        envio_dict, price = asyncio.create_task(parse_envios_async(envio))
        # envio_dict, price = asyncio.run(parse_envios_async(envio))
        # envio_dict, price = await parse_envios_async(envio)
        # date = envio.date_delivered.strftime("%d/%m/%Y")
        # total += envio.price
        # as_dict = {
        #     'destination': envio.full_address,
        #     'price': str(envio.price),
        #     'date_delivered': date,
        #     'detail': envio.get_detail_readable(),
        # }
        envios.append(envio_dict)
        total += price
    return envios, round(total), len(envios)


async def parse_envios_async(envio) -> Tuple[List[Any], Decimal]:
    date = envio.date_delivered.strftime("%d/%m/%Y")
    price = await calculate_price(envio)
    as_list = [date, envio.full_address,
               envio.get_detail_readable(), str(price), ]
    # as_dict = {
    #     'destination': envio.full_address,
    #     'price': str(price),
    #     'date_delivered': date,
    #     'detail': envio.get_detail_readable(),
    # }
    return as_list, price
