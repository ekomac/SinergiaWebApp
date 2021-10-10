import itertools
from typing import List
from operator import attrgetter
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

# ************************ TOWN ************************


def get_town_queryset(query=None):
    queryset = []
    queries = query.split(" ")
    queryset = itertools.chain(*map(map_as_town, queries))
    return list(set(queryset))


def map_as_town(q: str = '') -> List[Town]:
    """
    Returns a list of Town objects containing the q str
    in their properties.
    """
    return Town.objects.filter(
        Q(name__icontains=q) |
        Q(partido__name__icontains=q) |
        Q(delivery_code__code__icontains=q) |
        Q(flex_code__code__icontains=q)
    ).distinct()


def towns_view_2(request, *args, **kwargs):
    context = {}

    # Search
    query = ""
    print('get?')
    if request.method == 'GET':
        query = request.GET.get('q', '')
        context['query'] = str(query)

        towns = sorted(get_town_queryset(
            query), key=attrgetter('name'), reverse=False)

        print(len(towns))

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
    return render(request, "places/town/list.html", {})


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
