from typing import Callable
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponsePermanentRedirect
from envios.models import Envio


def allow_only_client(view_func) -> Callable or HttpResponsePermanentRedirect:
    def wrapper_func(request, *args, **kwargs):
        # User is in a group
        if request.user.groups.exists():
            # And that groups is Admins
            if request.user.groups.filter(name="Admins").exists():
                return view_func(request, *args, **kwargs)

            # And that groups is clients
            if request.user.groups.filter(name="Clients").exists():
                # And the envio's client is the same as the user's client
                pk = kwargs.get("pk", None)
                if pk:
                    envio = Envio.objects.get(pk=pk)
                    if envio.client is not None \
                            and request.user.client is not None:
                        if envio.client == request.user.client:
                            # If the envio's client is the same as the
                            # user's client, then the user is allowed to
                            # access the envio's page
                            return view_func(request, *args, **kwargs)
        raise PermissionDenied("No estás autorizado")
    return wrapper_func


def allow_only_client_in_class_view(view_func):
    """
    Allow envios only for propietary clients in class based views.
    """
    def wrapper_func(instance, request, *args, **kwargs):
        # User is in a group
        if request.user.groups.exists():
            # And that groups is Admins
            if request.user.groups.filter(name="Admins").exists():
                return view_func(instance, request, *args, **kwargs)
            # And that groups is clients
            if request.user.groups.filter(name="Clients").exists():
                # And the envio's client is the same as the user's client
                pk = kwargs.get("pk", None)
                if pk:
                    envio = Envio.objects.get(pk=pk)
                    if envio.client is not None \
                            and request.user.client is not None:
                        if envio.client == request.user.client:
                            # If the envio's client is the same as the
                            # user's client, then the user is allowed to
                            # access the envio's page
                            return view_func(
                                instance, request, *args, **kwargs)
        raise PermissionDenied("No estás autorizado")
    return wrapper_func
