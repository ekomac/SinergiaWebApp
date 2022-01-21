from account.models import Account
from deposit.models import Deposit
from envios.models import Envio
from tracking.models import TrackingMovement


def create_withdraw_movement(
        author,
        from_deposit: Deposit,
        to_carrier: Account
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
    )
    movement.save()
    return movement


def add_and_udpate_envios(
    movement: TrackingMovement,
    from_deposit: Deposit,
    to_carrier: Account,
    **filters
) -> None:
    """
    Adds and updates the envios of a movement.
    """
    envios = Envio.objects.filter(
        status__in=[Envio.STATUS_NEW, Envio.STATUS_STILL],
        deposit=from_deposit,
        **filters
    )
    # Add envios to the movement
    movement.envios.add(*envios)
    envios.update(
        status=Envio.STATUS_MOVING,
        carrier=to_carrier,
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
    movement = create_withdraw_movement(author, from_deposit, to_carrier)
    add_and_udpate_envios(movement, from_deposit, to_carrier)
    return movement


def withdraw_by_ids(
    author,
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
    movement = create_withdraw_movement(author, from_deposit, to_carrier)
    add_and_udpate_envios(movement, from_deposit, to_carrier, id__in=ids)
    return movement


def withdraw_by_town_ids(
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
    movement = create_withdraw_movement(author, from_deposit, to_carrier)
    add_and_udpate_envios(movement, from_deposit,
                          to_carrier, town__id__in=town_ids)
    return movement


def withdraw_by_partido_ids(
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
    movement = create_withdraw_movement(author, from_deposit, to_carrier)
    add_and_udpate_envios(movement, from_deposit,
                          to_carrier, town__partido__id__in=partido_ids)
    return movement


def withdraw_by_zone_ids(
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
    movement = create_withdraw_movement(author, from_deposit, to_carrier)
    add_and_udpate_envios(movement, from_deposit,
                          to_carrier, town__partido__zone__id__in=zone_ids)
    return movement
