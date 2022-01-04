from django.shortcuts import redirect


def ticket_safe(
        roles=[], redirect_app: str = None, *redirect_args, **redirect_kwargs
):
    """
    Gentyle (and safely) redirects the user if he is not allowed to access
    the app_transfer app, when he isn't carrying something and it's not
    allowed to transfer in name of others.

    Args:
        roles (list, optional): If user isn't carrying something, is allowed to
        transfer in name of other if he/she belongs to one ore more roles.
        Defaults to [].
        redirect_app (callable, optional): execute this function when
        user can't transfer. Defaults to None.
    """
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            # If the user has tickets
            has_tickets = request.user.ticket_set.count() > 0
            # If the user isn't carrying something and has an appropiate role
            if not has_tickets and request.user.groups.exists() and \
                    not request.user.groups.all().filter(
                        name__in=roles).exists():
                # And the redirect is correctly provided
                if not redirect_app:  # (Implicit booleaness)
                    raise ValueError("redirect_app is required")
                # Redirect to the appropiate app
                return redirect(
                    redirect_app, *redirect_args, **redirect_kwargs)
            # If the user is carrying something or has an appropiate role
            # Execute the function as intended
            return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator
