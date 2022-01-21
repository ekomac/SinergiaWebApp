from account.models import Account
from deposit.models import Deposit
from envios.models import Envio
from tracking.models import TrackingMovement


def create_deposit_movement(
    author,
    from_carrier: Account,
    to_deposit: Deposit
) -> TrackingMovement:
    """
    Creates a movement for the deposit action.

    Args:
        author (Account): the Account performing the action.
        from_carrier (Account): Account carrying the envios being deposited.
        to_deposit (Deposit): the Deposit where the envios will be deposited.

    Returns:
        TrackingMovement: the created and saved movement.
    """
    movement = TrackingMovement(
        created_by=author,
        from_carrier=from_carrier,
        to_deposit=to_deposit,
        action=TrackingMovement.ACTION_DEPOSIT,
        result=TrackingMovement.RESULT_IN_DEPOSIT,
    )
    movement.save()
    return movement


def add_and_udpate_envios(
    movement: TrackingMovement,
    from_carrier: Account,
    to_deposit: Deposit,
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
    movement.envios.add(*envios)
    envios.update(
        status=Envio.STATUS_STILL,
        deposit=to_deposit,
        carrier=None,
    )


def deposit_all(
    author,
    from_carrier: Account,
    to_deposit: Deposit,
) -> TrackingMovement:
    """
    Performs a deposit action, creating a movement and updating
    the envios' status. The deposit is performed for all envios
    from the given carrier.

    Args:
        author (Account): the Account performing the action.
        from_carrier (Account): the Account carrying the envios being
        deposited.
        to_deposit (Deposit): the Deposit where the envios will be deposited.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_deposit_movement(author, from_carrier, to_deposit)
    add_and_udpate_envios(movement, from_carrier, to_deposit)
    return movement


def deposit_by_ids(
    author,
    from_carrier: Account,
    to_deposit: Deposit,
    *ids: int
) -> TrackingMovement:
    """
    Performs a deposit action, creating a movement and updating
    the envios' status. The deposit is performed for all envios
    which ids where given.

    Args:
        author (Account): the Account performing the action.
        from_carrier (Account): the Account carrying the envios being
        deposited.
        to_deposit (Deposit): the Deposit where the envios will be deposited.
        ids (Tuple[int]): the ids of the envios to be deposited.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_deposit_movement(author, from_carrier, to_deposit)
    add_and_udpate_envios(movement, from_carrier, to_deposit, id__in=ids)
    return movement


def deposit_by_town_ids(
    author: Account,
    from_carrier: Account,
    to_deposit: Deposit,
    *town_ids: int
) -> TrackingMovement:
    """
    Performs a deposit action, creating a movement and updating
    the envio's status. The deposit is performed for all envios
    which's town id is given.

    Args:
        author (Account): the Account performing the action.
        from_carrier (Account): Account carrying the envios being deposited.
        to_deposit (Deposit): the Deposit where the envios will be deposited.
        town_ids (Tuple[int]): the ids of the towns to use to filter.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_deposit_movement(author, from_carrier, to_deposit)
    add_and_udpate_envios(movement, from_carrier,
                          to_deposit, town__id__in=town_ids)
    return movement


def deposit_by_partido_ids(
    author: Account,
    from_carrier: Account,
    to_deposit: Deposit,
    *partido_ids: int
) -> TrackingMovement:
    """
    Performs a deposit action, creating a movement and updating
    the envio's status. The deposit is performed for all envios
    which's town's partido id is given.

    Args:
        author (Account): the Account performing the action.
        from_carrier (Account): Account carrying the envios being deposited.
        to_deposit (Deposit): the Deposit where the envios will be deposited.
        partido_ids (Tuple[int]): the ids of the partidos to use to filter.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_deposit_movement(author, from_carrier, to_deposit)
    add_and_udpate_envios(movement, from_carrier, to_deposit,
                          town__partido__id__in=partido_ids)
    return movement


def deposit_by_zone_ids(
    author: Account,
    from_carrier: Account,
    to_deposit: Deposit,
    *zone_ids: int
) -> TrackingMovement:
    """
    Performs a deposit action, creating a movement and updating
    the envio's status. The deposit is performed for all envios
    which's town's partido's zone id is given.

    Args:
        author (Account): the Account performing the action.
        from_carrier (Account): Account carrying the envios being deposited.
        to_deposit (Deposit): the Deposit where the envios will be deposited.
        zone_ids (Tuple[int]): the ids of the partidos to use to filter.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_deposit_movement(author, from_carrier, to_deposit)
    add_and_udpate_envios(movement, from_carrier, to_deposit,
                          town__partido__zone__id__in=zone_ids)
    return movement
