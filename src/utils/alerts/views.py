from typing import Any
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.base import View
from datetime import datetime
from .alert import ToastAlert

# Topics
TOPIC_CREATE = 'create'
TOPIC_UDPATE = 'update'
TOPIC_DELETE = 'delete'

# Statuses
STATUS_SUCCESS = 'success'
STATUS_PENDING = 'pending'
STATUS_ERROR = 'error'

# Default titles
DEFAULT_CREATE_CORRECT_TITLE = 'Creación correcta'
DEFAULT_UPDATE_CORRECT_TITLE = 'Actualización correcta'
DEFAULT_DELETE_CORRECT_TITLE = 'Eliminación correcta'
DEFAULT_CREATE_INCORRECT_TITLE = 'Creación incorrecta'
DEFAULT_UPDATE_INCORRECT_TITLE = 'Actualización incorrecta'
DEFAULT_DELETE_INCORRECT_TITLE = 'Eliminación incorrecta'
DEFAULT_CREATE_PENDING_TITLE = 'Creación pendiente'
DEFAULT_UPDATE_PENDING_TITLE = 'Actualización pendiente'
DEFAULT_DELETE_PENDING_TITLE = 'Eliminación pendiente'


def get_topics():
    return [TOPIC_CREATE, TOPIC_UDPATE, TOPIC_DELETE]


def get_statuses():
    return [STATUS_SUCCESS, STATUS_PENDING, STATUS_ERROR]


class BaseAlert(object):

    def add_alert(self, request: HttpRequest, **kwargs):
        """Adds an alert to request's session
        indicating the result of an action"""
        # Check if needed kwargs are present
        for key in ['topic', 'status', 'title', 'msg']:
            if key not in kwargs.keys():
                raise ValueError(f'Please, provide a {key}.')
        # Gets current alerts
        alerts = request.session.get('alerts', [])
        # Get current time
        now = datetime.now()
        # Create the alert
        alert = ToastAlert(kwargs['topic'], kwargs['status'],
                           kwargs['title'], kwargs['msg'], now)
        # Append it to already existing ones
        alerts.append(alert.get_as_dict())
        # Set them back to request's session
        request.session['alerts'] = alerts
        return request


# class Alerter(BaseAlert):

#     titles = {
#         'success': {TOPIC_CREATE: 'Creación correcta',
#                     TOPIC_UDPATE: 'Actualización correcta',
#                     TOPIC_DELETE: 'Eliminación correcta', },
#         'error': {TOPIC_CREATE: 'Creación incorrecta',
#                   TOPIC_UDPATE: 'Actualización incorrecta',
#                   TOPIC_DELETE: 'Eliminación incorrecta', },
#     }

#     def __init__(self, request: HttpRequest):
#         self.request = request

#     def __get_title(self, topic: str, status: str) -> str:
#         """Gets the title corresponding to topic and status.

#         Args:
#             topic (str): 'create', 'udapte' or 'delete'.
#             status (str): 'success' or 'error'.

#         Raises:
#             KeyError: if topic wasn't found.

#         Returns:
#             str: the title.
#         """
#         try:
#             title = self.titles[status][topic]
#             return title
#         except KeyError:
#             suggestion = "Try with 'create', 'udapte' or 'delete'."
#             raise KeyError(f'Given topic is invalid. {suggestion}')

#     def success_alert(self, topic: str, msg: str):
#         return self.__alert(topic, msg, 'success')

#     def error_alert(self, topic: str, msg: str):
#         return self.__alert(topic, msg, 'error')

#     def __alert(self, topic: str, msg: str, status):
#         title = self.__get_title(topic, status)
#         return super().add_alert(
#             self.request, topic=topic, status=status, title=title, msg=msg)

# def dispatch_error_alert(topic: str, message: str):
#     """Decorator for functions (or function based views) which need to add
#     an error alert to the HttpRequest.session property indicating the error.

#     Args:
#         topic (str): What the original action was about: create,
#         update or delete.
#         message (str): to display to the user.
#     """
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             request = args[0]
#             if type(request) is not HttpRequest:
#                 name = 'django.http.HttpRequest'
#                 error = f"The first argument must be of type {name}"
#                 raise TypeError(error)
#             titles = {
#                 TOPIC_CREATE: 'Creación incorrecta',
#                 TOPIC_UDPATE: 'Actualización incorrecta',
#                 TOPIC_DELETE: 'Eliminación incorrecta',
#             }
#             try:
#                 title = titles[topic]
#             except KeyError:
#                 raise KeyError('Given topic is invalid.')
#             args[0] = BaseAlert().add_alert(
#                 args[0], topic=topic, status='error',
#                 title=title, msg=message
#             )
#             args[0] = request
#             return func(**args, **kwargs)
#         return wrapper
#     return decorator


class BaseAlertViewMixin(BaseAlert, View):

    def add_alert(self, **kwargs):
        """Adds an alert to request's session
        indicating the result of an action"""
        return super().add_alert(self.request, **kwargs)


class SuccessfulCreationAlertMixin(BaseAlertViewMixin):

    def add_alert(self, msg):
        """Adds an alert to request's session indicating the create action"""
        return super().add_alert(
            topic='create', status='success',
            title='Creación correcta', msg=msg)


class SuccessfulUpdateAlertMixin(BaseAlertViewMixin):

    def add_alert(self, msg):
        """Adds an alert to request's session indicating the create action"""
        return super().add_alert(
            topic='update', status='success',
            title='Actualización correcta', msg=msg)


class SuccessfulDeletionAlertMixin(BaseAlertViewMixin):

    def add_alert(self, msg):
        """Adds an alert to request's session indicating the delete action"""
        return super().add_alert(
            topic='delete', status='success',
            title='Eliminación correcta', msg=msg)


def create_alert_and_redirect(
    request: HttpResponse,
    msg: str,
    url: str,
    id: Any = None
) -> HttpResponseRedirect:
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
    if id:
        return redirect(url, id)
    return redirect(url)


def update_alert_and_redirect(
    request: HttpResponse,
    msg: str,
    url: str,
    id: Any = None
) -> HttpResponseRedirect:
    """Returns an HttpResponse form a redirect but adds an
    alert to notify an update successful to request.

    Args:
        request (HttpResponse): the request from a django function based view.
        msg (str): to pass to the alert (ToastAlert obj).
        url (str): django's url formatted.
        id (Any): the id of the object updated.

    Returns:
        HttpResponseRedirect: the redirect function which returns this object.
    """
    # Gets current alerts
    alerts = request.session.get('alerts', [])
    # Get current time
    now = datetime.now()
    # Create the alert
    alert = ToastAlert('update', 'success',
                       'Actualización correcta', msg, now)
    # Append it to already existing ones
    alerts.append(alert.get_as_dict())
    # Set them back to request's session
    request.session['alerts'] = alerts
    if id:
        return redirect(url, id)
    return redirect(url)
