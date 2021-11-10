from typing import List
from envios.models import Envio, TrackingMovement


def withdraw_movement(
    carrier,
    client=None,
    deposit=None,
    envios_ids: List[int] = [],
    **filters
) -> None:

    # Create the movement
    movement = TrackingMovement(
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
        movement.envios.add(*envios)

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
    carrier,
    client=None,
    deposit=None,
    **filters


) -> None:
    pass


def update_envio_movement(
    carrier,
    client=None,
    deposit=None,
    **filters
) -> None:
    pass


def envios_filtered(*ids, **filters):
    if ids:
        return Envio.objects.filter(id__in=list(ids))
    if filters:
        Envio.objects.filter(**filters)
        pass
    raise Envio.DoesNotExist
