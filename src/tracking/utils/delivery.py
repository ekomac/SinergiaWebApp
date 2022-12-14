from typing import Tuple
from account.models import Account
from envios.models import Envio
from tracking.models import TrackingMovement


def delivery_attempt(
        author: Account,
        result_obtained: str,
        envio_tracking_id: int,
        receiver_doc_id: str = None,
        proof_file=None,
        comment: str = ""
) -> Tuple[TrackingMovement, Envio]:
    """
    Creates a movement for the intended delivery action.

    Args:
        author (Account): the Account performing the action
        and carrying the envio.
        result_obtained (str): the result obtained by the carrier.
        envio_tracking_id (int): the tracking id of the envio to be delivered.
        receiver_doc_id (str): the document id of the person who received.
        proof_file ([File], optional): the proof file to be uploaded.
        Defaults to None.
        comment (str, optional): the comment to be added to the movement.
        Defaults to "".

    Returns:
        TrackingMovement: the created and saved movement.
    """
    # Create the movement
    movement = TrackingMovement(
        created_by=author,
        from_carrier=author,
        action=TrackingMovement.ACTION_DELIVERY_ATTEMPT,
        receiver_doc_id=receiver_doc_id,
        result=result_obtained,
        proof=proof_file,
        comment=comment,
    )
    movement.save()

    envios = Envio.objects.filter(tracking_id=envio_tracking_id)

    # Add envios to the movement
    movement.envios.add(*envios)

    envios.update(has_delivery_attempt=True)

    if result_obtained == TrackingMovement.RESULT_DELIVERED:
        envios.update(
            status=Envio.STATUS_DELIVERED,
            carrier=None,
            deposit=None,
            deliverer=author,
            date_delivered=movement.date_created,
            updated_by=movement.created_by
        )
    return movement, envios[0]


def indirect_successfull_delivery(
    author: Account,
    deliverer: Account,
    result_obtained: str,
    envio_tracking_id: int,
    receiver_doc_id: str = None,
    proof_file=None,
    comment: str = ""
) -> Envio:
    """
    Performs an indirect successfull delivery action, creating a movement and
    updating the envio status.
    The author corresponds to the Account that performed the save action, and
    the carrier to the one performing the actual action (deliverer).

    Args:
        author (Account): the Account performing the saving action.
        carrier (Account): the Account that performed the action.
        result_obtained (str): the result obtained by the carrier.
        envio_tracking_id (int): the tracking id of the envio to be delivered.
        receiver_doc_id (str): the document id of the person who received.
        proof_file ([type], optional): the proof file to be uploaded.
        Defaults to None.
        comment (str, optional): the comment to be added to the movement.
        Defaults to "".

    Returns:
        Envio: [description]
    """
    comment = comment + \
        f" (Intento de entrega indirecto realizado por {author.username})"

    # Create the movement
    movement = TrackingMovement(
        created_by=author,
        from_carrier=deliverer,
        action=TrackingMovement.ACTION_DELIVERY_ATTEMPT,
        receiver_doc_id=receiver_doc_id,
        result=result_obtained,
        proof=proof_file,
        comment=comment
    )
    movement.save()

    envios = Envio.objects.filter(tracking_id=envio_tracking_id)

    # Add envios to the movement
    movement.envios.add(*envios)

    envios.update(has_delivery_attempt=True)

    if result_obtained == TrackingMovement.RESULT_DELIVERED:
        envios.update(
            status=Envio.STATUS_DELIVERED,
            carrier=None,
            deposit=None,
            deliverer=deliverer,
            date_delivered=movement.date_created,
            updated_by=movement.created_by
        )
    return (movement, envios[0])
