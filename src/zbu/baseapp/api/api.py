from typing import List
from account.models import Account
# from clients.models import Client
from envios.models import Envio
from tracking.models import TrackingMovement
from places.models import Deposit


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
    print("deposited")
    return


def transfer_movement() -> None:
    pass


def delivery_attempt() -> None:
    pass


def update_envio_movement(
    carrier,
    client=None,
    deposit=None,
    **filters
) -> None:
    pass
