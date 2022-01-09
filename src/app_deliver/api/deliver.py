from account.models import Account
from envios.models import Envio
from tracking.models import TrackingMovement


def delivery_movement(
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
