

from django.shortcuts import redirect
from django.urls import reverse


class HasToResetPasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if (
            request.path != reverse('reset-password')
            and '/api/' not in request.path
            and request.path != reverse('login')
            and request.path != reverse('logout')
        ):
            if request.user.is_authenticated:
                if request.user.has_to_reset_password:
                    return redirect(reverse('reset-password'))
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return response
