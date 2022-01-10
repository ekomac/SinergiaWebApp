from datetime import datetime
from typing import Any, Dict
from account.models import Account
from clients.models import Client
from tracking import TrackingMovement


def summarize_by_client(
    client: Client,
    date_from: datetime,
    date_to: datetime
) -> Dict[str, Dict[str, Any]]:
    """
    Summarizes the delivered envios from a client between two dates.
    Also, the Dict contains the input data and the total price of the Envios.

    Args:
        client (Client): the Client to whom the shipments belong.
        date_from (datetime): the date from which the envios will be
        summarized. Includes the date.
        date_to (datetime): the date until which the envios will be
        summarized. Includes the date_to.

    Returns:
        Dict[str, Dict[str, Any]]: a dictionary with the summary.
    """

    # Get the envios from the client
    movements = TrackingMovement.objects.filter(
        action=TrackingMovement.ACTION_DELIVERY_ATTEMPT,
        result=TrackingMovement.RESULT_DELIVERED,
        envios__client__id=client.pk,
        date_created__gte=date_from,
        date_created__lte=date_to
    ).order_by('-date_created')
    result = {}
    envios = []
    total = 0
    for movement in movements:
        for envio in movement.envios.all():
            envio = {
                'id': envio.id,
                'date_delivered': movement.date_created,
                'price': envio.price,
                'detail': envio.readable_detail,
                'type': envio.shimpent_type
            }
            total += envio['price']
            envios.append(envio)
    result['envios'] = envios
    result['total'] = total
    result['date_from'] = date_from
    result['date_to'] = date_to
    result['client'] = {'id': client.pk, 'name': client.name}
    return result


def summarize_by_deliverer(
    deliverer: Account,
    date_from: datetime,
    date_to: datetime
) -> Dict[str, Dict[str, int]]:
    """
    Summarizes the delivered envios from a deliverer between two dates.
    Also, the Dict contains the input data and the total price of the Envios.

    Args:
        deliverer (Account): the Client to be summarized.
        date_from (datetime): the date from which the envios will be
        summarized. Includes the date_from.
        date_to (datetime): the date until which the envios will be
        summarized. Includes the date_to.

    Returns:
        Dict[str, Dict[str, Any]]: a dictionary with the summarized envios.
    """

    # Get the envios from the client
    movements = TrackingMovement.objects.filter(
        carrier__id=deliverer.pk,
        action=TrackingMovement.ACTION_DELIVERY_ATTEMPT,
        result=TrackingMovement.RESULT_DELIVERED,
        date_created__gte=date_from,
        date_created__lte=date_to
    ).order_by('-date_created')
    result = {}
    envios = []
    total = 0
    for movement in movements:
        for envio in movement.envios.all().order_by('-date_delivered'):
            envio = {
                'id': envio.id,
                'date_delivered': movement.date_created,
                'price': envio.price,
                'detail': envio.readable_detail,
                'type': envio.shimpent_type
            }
            total += envio['price']
            envios.append(envio)
    result['envios'] = envios
    result['total'] = total
    result['date_from'] = date_from
    result['date_to'] = date_to
    result['deliverer'] = {'id': deliverer.id,
                           'name': deliverer.full_name_formal}
    return result
