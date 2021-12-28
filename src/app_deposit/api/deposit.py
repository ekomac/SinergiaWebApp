from typing import List
from account.models import Account
# from clients.models import Client
from envios.models import Envio, TrackingMovement
from places.models import Deposit


def deposit_movement(
    author: Account,
    carrier: Account,
    deposit: Deposit = None,
    envios_ids: List[int] = [],
    **filters
) -> None:

    print("depositing")
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
        print("depositing by scanned")
        envios = Envio.objects.filter(
            status=Envio.STATUS_MOVING,
            carrier=carrier,
        )

    # Specific ids where selected
    elif envios_ids:
        print("depositing by ids")
        envios = Envio.objects.filter(
            status=Envio.STATUS_MOVING,
            carrier=carrier,
            id__in=envios_ids
        )

    # Some filters where specified
    elif filters:
        print("depositing by filters")
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
    print("deposited")
    return
