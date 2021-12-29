from typing import List
from account.models import Account
from envios.models import Envio
from tracking.models import TrackingMovement


def transfer_movement(
    author: Account,
    carrier: Account,
    receiver=Account,
    envios_ids: List[int] = [],
    **filters
) -> None:

    # Create the movement
    movement = TrackingMovement(
        created_by=author,
        carrier=receiver,
        action=TrackingMovement.ACTION_TRANSFER,
        result=TrackingMovement.RESULT_TRANSFERED,
    )
    movement.save()

    # No envios, no filters, all envios from carrier are selected
    if not envios_ids and not filters:
        envios = Envio.objects.filter(
            status=Envio.STATUS_MOVING,
            carrier=carrier
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
        status=Envio.STATUS_MOVING,
        carrier=receiver,
        deposit=None,
    )
