import unidecode
from typing import List

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.urls import reverse

from alerts.views import UpdateAlertMixin

from places.models import Town
from places.forms import UpdateTownForm

BLOG_POSTS_PER_PAGE = 30
ORDERING = {
    'town': 'name',
    'town_desc': '-name',
    'partido': 'partido__name',
    'partido_desc': '-partido__name',
    'delivery': 'delivery_code__code',
    'delivery_desc': '-delivery_code__code',
    'flex': 'flex_code__code',
    'flex_desc': '-flex_code__code',
    None: 'partido__name',
}

# ************************ TOWN ************************


def get_town_queryset(
        query: str = None, order_by_key: str = None) -> List[Town]:
    """Get all towns that match provided query, if any. If none is given,
    returns all towns. Also, performs the query in the specified order.

    Args:
        query (str, optional): words to match the query. Defaults to empyt str.
        order_by_key (str, optional): to perform ordery by.
        Defaults to None.

    Returns:
        List[Town]: a list containing the towns which match at least one query.
    """
    query = unidecode.unidecode(query) if query else ""
    return list(Town.objects.filter(
        Q(name__icontains=query) |
        Q(partido__name__icontains=query) |
        Q(delivery_code__code__icontains=query) |
        Q(flex_code__code__icontains=query)
    ).order_by(ORDERING[order_by_key]).distinct())


@login_required(login_url='/login/')
def towns_view(request, *args, **kwargs):
    context = {}

    # Search
    query = ""
    if request.method == 'GET':
        query = request.GET.get('q', None)
        if query:
            context['query'] = str(query)

        order_by = request.GET.get('order_by', None)
        if order_by:
            context['order_by'] = str(order_by)

        towns = get_town_queryset(query, order_by)

        # Pagination
        page = request.GET.get('page', 1)
        towns_paginator = Paginator(towns, BLOG_POSTS_PER_PAGE)
        try:
            towns = towns_paginator.page(page)
        except PageNotAnInteger:
            towns = towns_paginator.page(BLOG_POSTS_PER_PAGE)
        except EmptyPage:
            towns = towns_paginator.page(
                towns_paginator.num_pages)

        context['towns'] = towns
        context['totalTowns'] = len(towns)
        context['selected_tab'] = 'places-tab'

    return render(request, "places/town/list.html", context)


class TownDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = Town
    template_name = "places/town/detail.html"


class TownUpdateView(UpdateAlertMixin, LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    form_class = UpdateTownForm
    template_name = "places/town/edit.html"

    def get_context_data(self, **kwargs):
        ctx = super(TownUpdateView, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'places-tab'
        return ctx

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Town, id=id_)

    def form_valid(self, form):
        self.add_alert(
            msg=f'La localidad "{form.instance.name.title()}" ' +
                'se actualizó correctamente',
        )
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('places:town-detail', kwargs={'pk': self.object.pk})


def town_delete(request, *args):
    return render(request, '', {})


# ************************ PARTIDO ************************


# ************************ ZONE ************************
