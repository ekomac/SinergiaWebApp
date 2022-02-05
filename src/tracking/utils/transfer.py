from account.models import Account
from envios.models import Envio
from tracking.models import TrackingMovement


def create_transfer_movement(
        author,
        from_carrier: Account,
        to_carrier: Account,
        label: str
) -> TrackingMovement:
    """
    Creates a movement for the withdraw action.

    Args:
        author (Account): the Account performing the action.
        from_deposit (Deposit): the Deposit where the envios will be
        deposited.
        to_carrier (Account): the Account that will withdraw the envios.

    Returns:
        TrackingMovement: the created and saved movement.
    """
    movement = TrackingMovement(
        created_by=author,
        from_carrier=from_carrier,
        to_carrier=to_carrier,
        action=TrackingMovement.ACTION_TRANSFER,
        result=TrackingMovement.RESULT_TRANSFERED,
        label=label
    )
    movement.save()
    return movement


def add_and_udpate_envios(
    movement: TrackingMovement,
    from_carrier: Account,
    to_carrier: Account,
    **filters
) -> None:
    """
    Adds and updates the envios of a movement.
    """
    envios = Envio.objects.filter(
        status__in=[Envio.STATUS_MOVING],
        carrier=from_carrier,
        **filters
    )
    # Add envios to the movement
    movement.envios.add(*envios)
    envios.update(
        status=Envio.STATUS_MOVING,
        carrier=to_carrier,
        deposit=None,
        updated_by=movement.created_by
    )


def transfer_all(
    author,
    from_carrier: Account,
    to_carrier: Account
) -> TrackingMovement:
    """
    Performs a transfer action, creating a movement and updating
    the envios' status. The transfer is performed for all envios
    from the former carrier.

    Args:
        author (Account): the Account performing the action.
        from_carrier (Account): the Account which from the
        envios are transfered.
        to_carrier (Account): the Account that receives the envios.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_transfer_movement(
        author, from_carrier, to_carrier, TrackingMovement.LABEL_ALL)
    add_and_udpate_envios(movement, from_carrier, to_carrier)
    return movement


def transfer_by_envios_tracking_ids(
    author,
    from_carrier: Account,
    to_carrier: Account,
    *tracking_ids: int
) -> TrackingMovement:
    """
    Performs a transfer action, creating a movement and updating
    the envios' status. The transfer is performed for all envios
    which tracking_ids where given.

    Args:
        author (Account): the Account performing the action.
        from_carrier (Account): the Account which from the
        envios are transfered.
        to_carrier (Account): the Account that receives the envios.
        tracking_ids (Tuple[int]): the tracking_ids of the envios
        to be transfered.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_transfer_movement(
        author, from_carrier, to_carrier, TrackingMovement.LABEL_BY_ENVIOS_IDS)
    add_and_udpate_envios(movement, from_carrier,
                          to_carrier, tracking_id__in=tracking_ids)
    return movement


def transfer_by_towns_ids(
    author: Account,
    from_carrier: Account,
    to_carrier: Account,
    *town_ids: int
) -> TrackingMovement:
    """
    Performs a transfer action, creating a movement and updating
    the envios' status. The transfer is performed for all envios
    which's town id is given.

    Args:
        author (Account): the Account performing the action.
        from_carrier (Account): the Account which from the
        envios are transfered.
        to_carrier (Account): the Account that receives the envios.
        town_ids (Tuple[int]): the ids of the towns to use to filter.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_transfer_movement(
        author, from_carrier, to_carrier, TrackingMovement.LABEL_BY_TOWNS_IDS)
    add_and_udpate_envios(movement, from_carrier,
                          to_carrier, town__id__in=town_ids)
    return movement


def transfer_by_partidos_ids(
    author: Account,
    from_carrier: Account,
    to_carrier: Account,
    *partido_ids
) -> TrackingMovement:
    """
    Performs a transfer action, creating a movement and updating
    the envios' status. The transfer is performed for all envios
    which's town's partido id is given.

    Args:
        author (Account): the Account performing the action.
        from_carrier (Account): the Account which from the
        envios are transfered.
        to_carrier (Account): the Account that receives the envios.
        partido_ids (Tuple[int]): the ids of the partidos to use to filter.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_transfer_movement(
        author, from_carrier, to_carrier,
        TrackingMovement.LABEL_BY_PARTIDOS_IDS)
    add_and_udpate_envios(movement, from_carrier,
                          to_carrier, town__partido__id__in=partido_ids)
    return movement


def transfer_by_zones_ids(
    author: Account,
    from_carrier: Account,
    to_carrier: Account,
    *zone_ids
) -> TrackingMovement:
    """
    Performs a transfer action, creating a movement and updating
    the envios' status. The transfer is performed for all envios
    which's town's partido's zone id is given.

    Args:
        author (Account): the Account performing the action.
        from_carrier (Account): the Account which from the
        envios are transfered.
        to_carrier (Account): the Account that receives the envios.
        zone_ids (Tuple[int]): the ids of the partidos to use to filter.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_transfer_movement(
        author, from_carrier, to_carrier, TrackingMovement.LABEL_BY_ZONES_IDS)
    add_and_udpate_envios(movement, from_carrier,
                          to_carrier, town__partido__zone__id__in=zone_ids)
    return movement
