from typing import List
from account.models import Account
from clients.models import Client
from envios.models import Deposit, Envio, TrackingMovement


def withdraw_movement(
    author: Account,
    carrier: Account,
    client=None,
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
            shipment_status=Envio.STATUS_NEW,
            client=client
        )
    # Specific ids where selected
    elif envios_ids:
        envios = Envio.objects.filter(
            shipment_status=Envio.STATUS_NEW,
            client=client,
            id__in=envios_ids
        )

    # Some filters where specified
    elif filters:
        envios = Envio.objects.filter(
            shipment_status=Envio.STATUS_NEW,
            client=client,
            ** filters
        )
        print(envios)

    # Add envios to the movement
    movement.envios.add(*envios)


def insert_movement(
    author: Account,
    carrier: Account,
    deposit: Deposit = None,
    envios_ids: List[int] = [],
    **filters
) -> None:
    # Create the movement
    movement = TrackingMovement(
        created_by=author,
        deposit=deposit,
        action=TrackingMovement.ACTION_DEPOSIT,
        result=TrackingMovement.RESULT_IN_DEPOSIT,
    )
    movement.save()

    # All envios from carrier are selected
    if not envios_ids and not filters:
        envios = Envio.objects.filter(
            shipment_status=Envio.STATUS_MOVING,
            carrier=carrier,
        )
    movement.envios.add(*envios)

    pass


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
