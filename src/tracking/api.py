from deposit.models import Deposit
from typing import List
from account.models import Account
from envios.models import Envio
from tracking.models import TrackingMovement


def delivery(
    author: Account,
    result_obtained: str,
    envio_id: str,
    proof_file=None,
    comment: str = ""
) -> None:
    # Create the movement
    movement = TrackingMovement(
        created_by=author,
        carrier=author,
        action=TrackingMovement.ACTION_DELIVERY_ATTEMPT,
        result=result_obtained,
        proof=proof_file,
        comment=comment
    )
    movement.save()

    envios = Envio.objects.filter(pk=envio_id)

    # Add envios to the movement
    movement.envios.add(*envios)

    if result_obtained == TrackingMovement.RESULT_DELIVERED:
        envios.update(
            status=Envio.STATUS_DELIVERED,
            carrier=None,
            deposit=None,
            date_delivered=movement.date_created
        )
    return envios[0]


def deposit(
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
        carrier=carrier,
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


def transfer(
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


def withdraw(
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
        deposit=deposit,
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

    # Add envios to the movement
    movement.envios.add(*envios)
    envios.update(
        status=Envio.STATUS_MOVING,
        carrier=carrier,
        deposit=deposit,
    )
