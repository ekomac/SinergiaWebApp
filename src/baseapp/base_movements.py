from envios.models import Envio


def withdraw_movement(
    carrier,
    client=None,
    deposit=None,
    *envio_ids,
    **filters
) -> None:
    # No filter, all envios from client are selcted
    if not d:

    pass


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
