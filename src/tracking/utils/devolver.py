from account.models import Account
from deposit.models import Deposit
from envios.models import Envio
from tracking.models import TrackingMovement


def create_devolver_movement(
    author,
    from_carrier: Account,
    to_deposit: Deposit,
    label: str
) -> TrackingMovement:
    """
    Creates a movement for the returning action.

    Args:
        author (Account): the Account performing the action.
        from_carrier (Account): Account carrying the envios being returned.
        to_deposit (Deposit): the Deposit where the envios will be returned to.

    Returns:
        TrackingMovement: the created and saved movement.
    """
    movement = TrackingMovement(
        created_by=author,
        from_carrier=from_carrier,
        to_deposit=to_deposit,
        action=TrackingMovement.ACTION_RETURN,
        result=TrackingMovement.RESULT_RETURNED,
        label=label
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
        status=Envio.STATUS_RETURNED,
        deposit=to_deposit,
        carrier=None,
        updated_by=movement.created_by
    )


def devolver_all(
    author,
    from_carrier: Account,
    to_deposit: Deposit,
) -> TrackingMovement:
    """
    Performs a returning action, creating a movement and updating
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
    movement = create_devolver_movement(
        author, from_carrier, to_deposit, TrackingMovement.LABEL_ALL)
    add_and_udpate_envios(movement, from_carrier, to_deposit)
    return movement


def devolver_by_envios_tracking_ids(
    author,
    from_carrier: Account,
    to_deposit: Deposit,
    *tracking_ids: int
) -> TrackingMovement:
    """
    Performs a returning action, creating a movement and updating
    the envios' status. The deposit is performed for all envios
    which tracking_ids where given.

    Args:
        author (Account): the Account performing the action.
        from_carrier (Account): the Account carrying the envios being
        deposited.
        to_deposit (Deposit): the Deposit where the envios will be deposited.
        tracking_ids (Tuple[int]): the tracking_ids of the envios to
        be deposited.

    Returns:
        TrackingMovement: the created movement.
    """
    movement = create_devolver_movement(
        author, from_carrier, to_deposit, TrackingMovement.LABEL_BY_ENVIOS_IDS)
    add_and_udpate_envios(movement, from_carrier,
                          to_deposit, tracking_id__in=tracking_ids)
    return movement


def devolver_by_towns_ids(
    author: Account,
    from_carrier: Account,
    to_deposit: Deposit,
    *town_ids: int
) -> TrackingMovement:
    """
    Performs a returning action, creating a movement and updating
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
    movement = create_devolver_movement(
        author, from_carrier, to_deposit, TrackingMovement.LABEL_BY_TOWNS_IDS)
    add_and_udpate_envios(movement, from_carrier,
                          to_deposit, town__id__in=town_ids)
    return movement


def devolver_by_partidos_ids(
    author: Account,
    from_carrier: Account,
    to_deposit: Deposit,
    *partido_ids: int
) -> TrackingMovement:
    """
    Performs a returning action, creating a movement and updating
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
    movement = create_devolver_movement(
        author, from_carrier, to_deposit,
        TrackingMovement.LABEL_BY_PARTIDOS_IDS)
    add_and_udpate_envios(movement, from_carrier, to_deposit,
                          town__partido__id__in=partido_ids)
    return movement


# def devolver_by_zones_ids(
#     author: Account,
#     from_carrier: Account,
#     to_deposit: Deposit,
#     *zone_ids: int
# ) -> TrackingMovement:
#     """
#     Performs a returning action, creating a movement and updating
#     the envio's status. The deposit is performed for all envios
#     which's town's partido's zone id is given.

#     Args:
#         author (Account): the Account performing the action.
#         from_carrier (Account): Account carrying the envios being deposited.
#         to_deposit (Deposit): the Deposit where the envios will be deposited.
#         zone_ids (Tuple[int]): the ids of the partidos to use to filter.

#     Returns:
#         TrackingMovement: the created movement.
#     """
#     movement = create_devolver_movement(
#         author, from_carrier, to_deposit, TrackingMovement.LABEL_BY_ZONES_IDS
# )
#     add_and_udpate_envios(movement, from_carrier, to_deposit,
#                           town__partido__zone__id__in=zone_ids)
#     return movement
