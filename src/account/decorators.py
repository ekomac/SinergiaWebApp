from django.core.exceptions import PermissionDenied


def allowed_users(roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.groups.exists():
                groups = request.user.groups.all()
                for group in groups:
                    if group.name in roles:
                        return view_func(request, *args, **kwargs)
            raise PermissionDenied("No estás autorizado")
        return wrapper_func
    return decorator


def allowed_users_in_class_view(roles=[]):
    def decorator(view_func):
        def wrapper_func(instance, request, *args, **kwargs):
            if request.user.groups.exists():
                groups = request.user.groups.all()
                for group in groups:
                    if group.name in roles:
                        return view_func(instance, request, *args, **kwargs)
            raise PermissionDenied("No estás autorizado")
        return wrapper_func
    return decorator
