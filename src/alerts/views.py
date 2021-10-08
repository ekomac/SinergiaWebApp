from django.views.generic.base import View
from datetime import datetime
from alerts.alert import ToastAlert


class CreateAlertMixin(View):

    def add_alert(self, **kwargs):
        """Adds an alert to request's session indicating the create action"""
        # Gets current alerts
        alerts = self.request.session.get('alerts', [])
        # Get current time
        now = datetime.now()
        # Create the alert
        alert = ToastAlert(kwargs['topic'], kwargs['status'],
                           kwargs['title'], kwargs['msg'], now)
        # Append it to already existing ones
        alerts.append(alert.get_as_dict())
        # Set them back to request's session
        self.request.session['alerts'] = alerts
        return
