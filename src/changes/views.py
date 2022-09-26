from datetime import datetime, timedelta
from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from account.decorators import allowed_users_in_class_view
from changes.models import Change

from utils.views import CompleteListView, sanitize_date


class ChangeListView(CompleteListView, LoginRequiredMixin):
    template_name = 'changes/list.html'
    model = Change
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
    )
    query_keywords = (
        'name__icontains',
        'description__icontains',
    )
    include_add_button = False

    @allowed_users_in_class_view(roles=["Admins"])
    def get(self, request):
        return super(ChangeListView, self).get(request)

    def get_context_data(self) -> Dict[str, Any]:
        context = super().get_context_data()
        context['selected_tab'] = 'changes-tab'
        now = datetime.now()
        year = str(now.year).zfill(4)
        month = str(now.month).zfill(2)
        day = str(now.day).zfill(2)
        context['max_selectable_date'] = f'{year}-{month}-{day}'
        return context


def detail_view(request, pk):
    if request.method == 'GET':
        change = get_object_or_404(Change, pk=pk)
        context = {
            'obj': change,
            'selected_tab': 'changes-tab',
        }
        change.readers.add(request.user)
        return render(request, 'changes/detail.html', context)
