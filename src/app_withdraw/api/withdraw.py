from typing import List
from account.models import Account
from envios.models import Envio
from deposit.models import Deposit
from tracking.models import TrackingMovement


def withdraw_movement(
    author: Account,
    carrier: Account,
    deposit=Deposit,
    envios_ids: List[int] = [],
    **filters
) -> None:

    # Create the movement
    movement = TrackingMovement(
        created_by=author,
        carrier=carrier,
        action=TrackingMovement.ACTION_RECOLECTION,
        result=TrackingMovement.RESULT_TRANSFERED,
    )
    movement.save()

    # No envios, no filters, all envios from client are selected
    if not envios_ids and not filters:
        envios = Envio.objects.filter(
            status__in=[Envio.STATUS_NEW, Envio.STATUS_STILL],
            deposit=deposit
        )

    # Specific ids where selected
    elif envios_ids:
        envios = Envio.objects.filter(
            status__in=[Envio.STATUS_NEW, Envio.STATUS_STILL],
            deposit=deposit,
            id__in=envios_ids
        )

    # Some filters where specified
    elif filters:
        envios = Envio.objects.filter(
            status__in=[Envio.STATUS_NEW, Envio.STATUS_STILL],
            deposit=deposit,
            **filters
        )
        print(envios)

    # Add envios to the movement
    movement.envios.add(*envios)
    envios.update(
        status=Envio.STATUS_MOVING,
        carrier=carrier,
        deposit=None,
    )
