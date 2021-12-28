from typing import Any
from django.shortcuts import redirect


def transfer_safe(roles=[], redirect_app: Any = None) -> Any:
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            is_carrier = request.user.Carrier.count() > 0
            # if is_carrier:
            # print("Is carrier")
            # return view_func(request, *args, **kwargs)
            if not is_carrier and request.user.groups.exists():
                if not request.user.groups.all().filter(
                        name__in=roles).exists():
                    # Implicit booleaness
                    if not redirect_app:
                        raise ValueError("redirect_app is required")
                    return redirect(redirect_app)
            return view_func(request, *args, **kwargs)
            # raise PermissionDenied("No estás autorizado")
        return wrapper_func
    return decorator
