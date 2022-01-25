from account.models import Account
from deposit.models import Deposit
from envios.models import Envio
from tracking.models import TrackingMovement


def create_withdraw_movement(
        author,
        from_deposit: Deposit,
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
        from_deposit=from_deposit,
        to_carrier=to_carrier,
        action=TrackingMovement.ACTION_COLLECTION,
        result=TrackingMovement.RESULT_COLECTED,
        label=label,
    )
    movement.save()
    return movement


def add_and_udpate_envios(movement: TrackingMovement, **filters) -> None:
    """
    Adds and updates the envios of a movement.
    """
    envios = Envio.objects.filter(
        status__in=[Envio.STATUS_NEW, Envio.STATUS_STILL],
        deposit=movement.from_deposit,
        **filters
    )
    # Add envios to the movement
    movement.envios.add(*envios)
    envios.update(
        updated_by=movement.created_by,
        status=Envio.STATUS_MOVING,
        carrier=movement.to_carrier,
        deposit=None
    )


def withdraw_all(
    author,
    from_deposit: Deposit,
    to_carrier: Account
) -> TrackingMovement:
    """
    Performs a withdraw action, creating a movement and updating
    the envios' status. The withdraw is performed for all envios
    from the deposit.

    Args:
        author (Account): the Account performing the action.
        from_deposit (Deposit): the Deposit where the envios will be
        withdrawn from.
        to_carrier (Account): the Account that will withdraw the envios.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_withdraw_movement(
        author, from_deposit, to_carrier, TrackingMovement.LABEL_ALL)
    add_and_udpate_envios(movement)
    return movement


def withdraw_by_envios_ids(
    author: Account,
    from_deposit: Deposit,
    to_carrier: Account,
    *ids: int
) -> TrackingMovement:
    """
    Performs a withdraw action, creating a movement and updating
    the envios' status. The withdraw is performed for all envios
    which ids where given.

    Args:
        author (Account): the Account performing the action.
        from_deposit (Deposit): the Deposit where the envios will be
        deposited.
        to_carrier (Account): the Account that will withdraw the envios.
        ids (Tuple[int]): the ids of the envios to be withdrawn.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_withdraw_movement(
        author, from_deposit, to_carrier, TrackingMovement.LABEL_BY_ENVIOS_IDS)
    add_and_udpate_envios(movement, id__in=ids)
    return movement


def withdraw_by_towns_ids(
    author: Account,
    from_deposit: Deposit,
    to_carrier: Account,
    *town_ids: int
) -> TrackingMovement:
    """
    Performs a withdraw action, creating a movement and updating
    the envio's status. The withdraw is performed for all envios
    which's town id is given.

    Args:
        author (Account): the Account performing the action.
        from_deposit (Deposit): the Deposit where the envios will be
        deposited.
        to_carrier (Account): the Account that will withdraw the envios.
        town_ids (Tuple[int]): the ids of the towns to use to filter.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_withdraw_movement(
        author, from_deposit, to_carrier, TrackingMovement.LABEL_BY_TOWNS_IDS)
    add_and_udpate_envios(movement, town__id__in=town_ids)
    return movement


def withdraw_by_partidos_ids(
    author: Account,
    from_deposit: Deposit,
    to_carrier: Account,
    *partido_ids
) -> TrackingMovement:
    """
    Performs a withdraw action, creating a movement and updating
    the envio's status. The withdraw is performed for all envios
    which's town's partido id is given.

    Args:
        author (Account): the Account performing the action.
        from_deposit (Deposit): the Deposit where the envios will be
        deposited.
        to_carrier (Account): the Account that will withdraw the envios.
        partido_ids (Tuple[int]): the ids of the partidos to use to filter.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_withdraw_movement(
        author, from_deposit, to_carrier,
        TrackingMovement.LABEL_BY_PARTIDOS_IDS)
    add_and_udpate_envios(movement, town__partido__id__in=partido_ids)
    return movement


def withdraw_by_zones_ids(
    author: Account,
    from_deposit: Deposit,
    to_carrier: Account,
    *zone_ids
) -> TrackingMovement:
    """
    Performs a withdraw action, creating a movement and updating
    the envio's status. The withdraw is performed for all envios
    which's town's partido's zone id is given.

    Args:
        author (Account): the Account performing the action.
        from_deposit (Deposit): the Deposit where the envios will be
        deposited.
        to_carrier (Account): the Account that will withdraw the envios.
        zone_ids (Tuple[int]): the ids of the partidos to use to filter.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_withdraw_movement(
        author, from_deposit, to_carrier, TrackingMovement.LABEL_BY_ZONES_IDS)
    add_and_udpate_envios(movement, town__partido__zone__id__in=zone_ids)
    return movement
