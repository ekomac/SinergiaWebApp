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
    """
    Performs a delivery attempt action, creating a movement and updating the
    envio status.

    Args:
        author (Account): the Account performing the action.
        result_obtained (str): the result obtained by the carrier.
        envio_id (str): the id of the envio to be delivered.
        proof_file ([type], optional): the proof file to be uploaded.
        Defaults to None.
        comment (str, optional): the comment to be added to the movement.
        Defaults to "".
    """
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


def indirect_delivery(
    author: Account,
    carrier: Account,
    result_obtained: str,
    envio_id: str,
    proof_file=None,
    comment: str = ""
) -> Envio:
    """
    Performs an indirect delivery attempt action, creating a movement and
    updating the envio status.
    The author corresponds to the Account that performed the save action, and
    the carrier to the one performing the action.

    Args:
        author (Account): the Account performing the saving action.
        carrier (Account): the Account that performed the action.
        result_obtained (str): the result obtained by the carrier.
        envio_id (str): the id of the envio to be delivered.
        proof_file ([type], optional): the proof file to be uploaded.
        Defaults to None.
        comment (str, optional): the comment to be added to the movement.
        Defaults to "".

    Returns:
        Envio: [description]
    """
    comment = comment + f" (Entrega indirecta realizada por {author.username})"

    # Create the movement
    movement = TrackingMovement(
        created_by=author,
        carrier=carrier,
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
    """
    Performs a deposit action, creating a movement and updating the envio
    status.

    Args:
        author (Account): the Account performing the action.
        carrier (Account): the Account that will deposit the envios.
        deposit (Deposit): the Deposit where the envios will be deposited.
        envios_ids (List[int], optional): the ids of the envios to be
        deposited. Defaults to [].
    """

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
    receiver: Account,
    envios_ids: List[int] = [],
    **filters
) -> None:
    """
    Performs a transfer action, creating a movement and updating
    the envio status.

    Args:
        author (Account): the Account performing the action.
        carrier (Account): the Account that will receive the envios.
        receiver (Account): the Account that will receive the envios and
        now becomes the carrier. Defaults to None.
        envios_ids (List[int], optional): the ids of the envios to be
        transferred. Defaults to [].
    """

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
    """
    Performs a withdraw action, creating a movement and updating
    the envio status.

    Args:
        author (Account): the Account performing the action.
        carrier (Account): the Account that will withdraw the envios.
        deposit ([type], optional): the Deposit where the envios will be
        deposited. Defaults to None.
        envios_ids (List[int], optional): the ids of the envios to be
        withdrawn. Defaults to [].
    """

    # Create the movement
    movement = TrackingMovement(
        created_by=author,
        carrier=carrier,
        deposit=deposit,
        action=TrackingMovement.ACTION_COLLECTION,
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

    return movement
