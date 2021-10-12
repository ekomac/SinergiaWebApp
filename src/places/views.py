from typing import List
import unidecode
# from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.shortcuts import render
from django.db.models import Q
from places.models import Town

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
    None: '-partido__name',
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


def towns_view_2(request, *args, **kwargs):
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

        for i, town in enumerate(towns):
            if i > 30:
                break
            print(town, 'partido de', town.partido.name)

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


class TownListView(LoginRequiredMixin, ListView):

    model = Town
    template_name = "places/towns_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_tab'] = 'places-tab'
        return context


def towns_view(request, *args, **kwargs):

    context = {}
    context['selected_tab'] = 'places-tab'

    if request.method == 'GET':
        context['towns'] = Town.objects.all()
        context['selected_tab'] = 'places-tab'

    return render(request, "places/towns_list.html", context)


class TownAddView(CreateView):
    pass


class TownDetailView(LoginRequiredMixin, DetailView):
    model = Town
    template_name = "places/town_detail.html"


class TownUpdateView(UpdateView):
    pass


def town_delete(request, *args):
    return render(request, '', {})


# ************************ PARTIDO ************************


# ************************ ZONE ************************
