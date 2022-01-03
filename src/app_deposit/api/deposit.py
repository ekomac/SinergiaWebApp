from typing import List
from account.models import Account
# from clients.models import Client
from envios.models import Envio
from tracking.models import TrackingMovement
from deposit.models import Deposit


def deposit_movement(
    author: Account,
    carrier: Account,
    deposit: Deposit = None,
    envios_ids: List[int] = [],
    **filters
) -> None:

    if deposit is None:
        raise ValueError('Deposit is required')

    # Create the movement
    movement = TrackingMovement(
        created_by=author,
        deposit=deposit,
        action=TrackingMovement.ACTION_DEPOSIT,
        result=TrackingMovement.RESULT_IN_DEPOSIT,
    )
    movement.save()

    # No envios, no filters, all envios from carrier are selected
    if not envios_ids and not filters:
        envios = Envio.objects.filter(
            status=Envio.STATUS_MOVING,
            carrier=carrier,
        )

    # Specific ids where selected
    elif envios_ids:
        envios = Envio.objects.filter(
            status=Envio.STATUS_MOVING,
            carrier=carrier,
            id__in=envios_ids
        )

    # Some filters where specified
    elif filters:
        envios = Envio.objects.filter(
            status=Envio.STATUS_MOVING,
            carrier=carrier,
            **filters
        )

    # Add envios to the movement
    movement.envios.add(*envios)
    envios.update(
        status=Envio.STATUS_STILL,
        deposit=deposit,
        carrier=None,
    )
    return
