from typing import Any
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.base import View
from datetime import datetime
from alerts.alert import ToastAlert


class BaseAlertMixin(View):

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


class CreateAlertMixin(BaseAlertMixin):

    def add_alert(self, msg):
        """Adds an alert to request's session indicating the create action"""
        return super().add_alert(
            topic='create', status='success',
            title='Creación correcta', msg=msg)


class UpdateAlertMixin(BaseAlertMixin):

    def add_alert(self, msg):
        """Adds an alert to request's session indicating the create action"""
        return super().add_alert(
            topic='update', status='success',
            title='Actualización correcta', msg=msg)


class DeleteAlertMixin(BaseAlertMixin):

    def add_alert(self, msg):
        """Adds an alert to request's session indicating the delete action"""
        return super().add_alert(
            topic='delete', status='success',
            title='Eliminación correcta', msg=msg)


def create_alert_and_redirect(request: HttpResponse, msg: str,
                              url: str, id: Any) -> HttpResponseRedirect:
    """Returns an HttpResponse form a redirect but adds an
    alert to notify creation successful to request.

    Args:
        request (HttpResponse): the request from a django function based view.
        msg (str): to pass to the alert (ToastAlert obj).
        url (str): django's url formatted.
        id (Any): the id of the object created.

    Returns:
        HttpResponseRedirect: the redirect function which returns this object.
    """
    # Gets current alerts
    alerts = request.session.get('alerts', [])
    # Get current time
    now = datetime.now()
    # Create the alert
    alert = ToastAlert('create', 'success',
                       'Creación correcta', msg, now)
    # Append it to already existing ones
    alerts.append(alert.get_as_dict())
    # Set them back to request's session
    request.session['alerts'] = alerts
    return redirect(url, id)
