from django.shortcuts import redirect


def deliver_safe(redirect_app: str = None, *redirect_args, **redirect_kwargs):
    """
    Gentyle (and safely) redirects the user if he is not allowed to access
    the app_deliver app when he isn't carrying something or when trying to
    deliver a Envio that is not carrying.

    Args:
        redirect_app (callable, optional): execute this function when
        user can't deliver. Defaults to None.
    """
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            # If the user is carrying a "Envío"
            is_carrier = request.user.envios_carried_by.count() > 0
            print("is_carrier", is_carrier)
            envio_id = request.GET.get('eid', None)
            # If the user isn't carrying something
            if not is_carrier or (is_carrier and envio_id is not None and
                                  not request.user.envios_carried_by.filter(
                                      pk=envio_id).exists()
                                  ):
                # And the redirect is correctly provided
                if not redirect_app:  # (Implicit booleaness)
                    raise ValueError("redirect_app is required")
                # Redirect to the appropiate app
                return redirect(
                    redirect_app, *redirect_args, **redirect_kwargs)
            # If the user is carrying something,
            # execute the function as intended
            return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator
