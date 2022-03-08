

from logger.models import Log


class LogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        try:
            if request.user.is_authenticated and request.user.is_superuser:
                if '/superadmin/' in request.path:
                    return self.get_response(request)
            Log(
                url=request.path,
                user=request.user,
            ).save()
        except Exception as e:
            Log(
                url=request.path,
                error=e
            ).save()
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return response
