from datetime import datetime, timedelta
from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from account.decorators import allowed_users_in_class_view
from account.models import Account
from deposit.models import Deposit
from tracking.models import TrackingMovement
from utils.views import CompleteListView, sanitize_date


class TrackingMovementsListView(CompleteListView, LoginRequiredMixin):
    template_name = 'tracking/list.html'
    model = TrackingMovement
    decoders = (
        {
            'key': 'min_date',
            'filter': 'date_created__gte',
            'function': sanitize_date,
            'context': lambda x: x,
        },
        {
            'key': 'max_date',
            'filter': 'date_created__lte',
            'function': lambda x: sanitize_date(x, True) + timedelta(days=1),
            'context': lambda x: x,
        },
        {
            'key': 'from_deposit_id',
            'filter': lambda x: 'from_deposit__isnull' if (
                x in [-1, '-1']) else 'from_deposit__id',
            'function': lambda x: True if x in [-1, '-1'] else int(x),
            'context': str,
        },
        {
            'key': 'to_deposit_id',
            'filter': lambda x: 'to_deposit__isnull' if (
                x in [-1, '-1']) else 'to_deposit__id',
            'function': lambda x: True if x in [-1, '-1'] else int(x),
            'context': str,
        },
        {
            'key': 'from_carrier_id',
            'filter': lambda x: 'from_carrier__isnull' if (
                x in [-1, '-1']) else 'from_carrier__id',
            'function': lambda x: True if x in [-1, '-1'] else int(x),
            'context': str,
        },
        {
            'key': 'to_carrier_id',
            'filter': lambda x: 'to_carrier__isnull' if (
                x in [-1, '-1']) else 'to_carrier__id',
            'function': lambda x: True if x in [-1, '-1'] else int(x),
            'context': str,
        },
        {
            'key': 'result',
            'filter': 'result',
            'function': lambda x: x,
            'context': lambda x: x,
        },
    )
    query_keywords = (
        'from_carrier__first_name__icontains',
        'from_carrier_id__last_name__icontains',
        'from_carrier_id__username__icontains',
        'from_carrier_id__email__icontains',
        'from_carrier_id__dni__icontains',
        'to_carrier__first_name__icontains',
        'to_carrier_id__last_name__icontains',
        'to_carrier_id__username__icontains',
        'to_carrier_id__email__icontains',
        'to_carrier_id__dni__icontains',
        'from_deposit__name__icontains',
        'from_deposit__client__name__icontains',
        'to_deposit__name__icontains',
        'to_deposit__client__name__icontains',
    )

    @allowed_users_in_class_view(roles=["Admins"])
    def get(self, request):
        return super(TrackingMovementsListView, self).get(request)

    def get_context_data(self) -> Dict[str, Any]:
        context = super().get_context_data()
        context['deposits'] = Deposit.objects.all()
        context['carriers'] = Account.objects.filter(
            groups__name__in=['Admins', "Level 1", "Level 2"])
        context['selected_tab'] = 'tracking-tab'
        now = datetime.now()
        year = str(now.year).zfill(4)
        month = str(now.month).zfill(2)
        day = str(now.day).zfill(2)
        context['max_selectable_date'] = f'{year}-{month}-{day}'
        return context
