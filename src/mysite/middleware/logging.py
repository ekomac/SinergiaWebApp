

from logger.models import Log


class LogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        if request:
            data = None
            if isinstance(request, dict):
                if 'data' in request:
                    data = str(request['data'])
                elif 'DATA' in request:
                    data = str(request['DATA'])
                elif 'POST' in request:
                    data = str(request['POST'])
                elif 'GET' in request:
                    data = str(request['GET'])
                else:
                    data = str(request)
            else:
                if hasattr(request, 'data'):
                    data = str(request.data)
                elif hasattr(request, 'DATA'):
                    data = str(request.DATA)
                elif hasattr(request, 'POST'):
                    data = str(request.POST)
                elif hasattr(request, 'GET'):
                    data = str(request.GET)
                else:
                    data = str(request)
            try:
                if request.user.is_authenticated and request.user.is_superuser:
                    if '/superadmin/' in request.path:
                        return self.get_response(request)
                Log(
                    url=request.path,
                    user=request.user,
                    data=data
                ).save()
            except Exception as e:
                Log(
                    url=request.path,
                    error=e,
                    data=data
                ).save()
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return response
