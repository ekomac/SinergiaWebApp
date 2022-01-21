from typing import List
from account.models import Account
from deposit.models import Deposit
from envios.models import Envio
from tracking.models import TrackingMovement

WITHDRAW_ALL_FLAG = 1
WITHDRAW_BY_IDS_FLAG = 2
WITHDRAW_BY_FILTER_FLAG = 3


def withdraw(
    flag: int,
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

    # No envios, no filters, all envios from deposit are selected
    if flag == WITHDRAW_ALL_FLAG:
        envios = Envio.objects.filter(
            status__in=[Envio.STATUS_NEW, Envio.STATUS_STILL],
            deposit=deposit
        )

    # Specific id where selected
    elif flag == WITHDRAW_BY_IDS_FLAG:
        envios = Envio.objects.filter(
            status__in=[Envio.STATUS_NEW, Envio.STATUS_STILL],
            deposit=deposit,
            id__in=envios_ids
        )

    # Some filters where specified
    elif flag == WITHDRAW_BY_FILTER_FLAG:
        if filters:
            envios = Envio.objects.filter(
                status__in=[Envio.STATUS_NEW, Envio.STATUS_STILL],
                deposit=deposit,
                **filters
            )
        else:
            raise ValueError(
                '''The flag was set to user withdraw by filters,
                but no filters where specified.''')

    else:
        raise ValueError(
            """
            Invalid flag value. Valid values are:
            WITHDRAW_ALL_FLAG: 1,
            WITHDRAW_SCANNED_FLAG: 2,
            WITHDRAW_MANY_FLAG: 3,
            WITHDRAW_BY_FILTER_FLAG: 4.
            """
        )

    # Add envios to the movement
    movement.envios.add(*envios)
    envios.update(
        status=Envio.STATUS_MOVING,
        carrier=carrier,
        deposit=None,
    )

    return movement
