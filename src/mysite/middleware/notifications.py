from changes.models import Change


class NotificationsMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            pks = [request.user.pk]
            request.notification_count = Change.objects.exclude(
                readers__in=pks).count()
        except Exception:
            request['notification_count'] = 0
        response = self.get_response(request)

        return response
