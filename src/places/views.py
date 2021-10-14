import unidecode
from typing import List

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.urls import reverse
from account.models import Account

from utils.alerts.views import (
    UpdateAlertMixin,
    create_alert_and_redirect
)

from places.models import Partido, Town, Zone
from places.forms import (
    AddZoneForm,
    UpdateTownForm,
    UpdateZoneForm,
    # UpdatePartidosZone,
)
from utils.views import DeleteObjectsUtil, ContextMixin

TOWNS_PER_PAGE = 30
ZONES_PER_PAGE = 30
TOWNS_ORDERING = {
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
ZONES_ORDERING = {
    'name': 'name',
    'name_desc': '-name',
    None: 'name',
}

# ************************ TOWN ************************


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
        towns_paginator = Paginator(towns, TOWNS_PER_PAGE)
        try:
            towns = towns_paginator.page(page)
        except PageNotAnInteger:
            towns = towns_paginator.page(TOWNS_PER_PAGE)
        except EmptyPage:
            towns = towns_paginator.page(towns_paginator.num_pages)

        context['towns'] = towns
        context['totalTowns'] = len(towns)
        context['selected_tab'] = 'town-tab'

    return render(request, "places/town/list.html", context)


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
    ).order_by(TOWNS_ORDERING[order_by_key]).distinct())


class TownDetailView(ContextMixin, LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = Town
    template_name = "places/town/detail.html"
    context = {'selected_tab': 'town-tab'}


class TownUpdateView(
        UpdateAlertMixin, ContextMixin, LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    form_class = UpdateTownForm
    template_name = "places/town/edit.html"
    context = {
        'selected_tab': 'town-tab'
    }

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


# ************************ ZONE ************************
@login_required(login_url='/login/')
def zones_view(request, *args, **kwargs):
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
        reverse = str(order_by) == 'name_desc'
        zones = get_zone_queryset(query, reverse=reverse)

        # Pagination
        page = request.GET.get('page', 1)
        zones_paginator = Paginator(zones, ZONES_PER_PAGE)
        try:
            zones = zones_paginator.page(page)
        except PageNotAnInteger:
            zones = zones_paginator.page(ZONES_PER_PAGE)
        except EmptyPage:
            zones = zones_paginator.page(zones_paginator.num_pages)

        context['zones'] = zones
        context['totalZones'] = len(zones)
        context['selected_tab'] = 'zone-tab'

    return render(request, "places/zone/list.html", context)


def get_zone_queryset(query: str = None, reverse: bool = False) -> List[Zone]:
    """Get all zones that match provided query, if any. If none is given,
    returns all zones. Also, performs the query in the specified order.

    Args:
        query (str, optional): words to match the query. Defaults to empyt str.
        order_by_key (str, optional): to perform ordery by.
        Defaults to None.

    Returns:
        List[Zone]: a list containing the zones which match at least one query.
    """
    query = unidecode.unidecode(query) if query else ""
    order_by = 'name'
    if reverse:
        order_by = '-name'
    return list(Zone.objects.filter(
        Q(name__icontains=query) |
        Q(asigned_to__first_name__icontains=query) |
        Q(asigned_to__last_name__icontains=query)
    ).order_by(order_by).distinct())


@login_required(login_url='/login/')
def add_zone_view(request, *args, **kwargs):
    context = {
        'selected_tab': 'zone-tab',
        'partidos': Partido.objects.all(),
        'partidosList': list(Partido.objects.all()),
        'partidosTotal': Partido.objects.count(),
    }

    form = AddZoneForm(request.POST or None)
    ids = request.POST.get('selected_partidos_ids', None)
    if form.is_valid():
        for key, value in request.POST.items():
            print(key, ":", value)
        obj = form.save(commit=False)
        author = Account.objects.filter(email=request.user.email).first()
        obj.updated_by = author
        obj.save()
        if ids:
            for id in ids.split("-"):
                partido = get_object_or_404(Partido, pk=id)
                partido.amba_zone = obj
                partido.save()
        form = AddZoneForm()
        msg = f'La zona {obj.name} se creó correctamente.'
        return create_alert_and_redirect(
            request, msg, 'places:zone-detail', obj.pk)

    context['form'] = form
    context['partidos_ids'] = ids

    return render(request, "places/zone/add.html", context)


class ZoneDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = Zone
    template_name = "places/zone/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_tab'] = 'zone-tab'
        context['total_partidos'] = self.object.partido_set.count()
        # partidos = self.object.partido_set.all()
        context['partidos'] = self.object.partido_set.all()
        # partidos = [partido.name.title() for partido in partidos]
        # context['partidos'] = ', '.join(partidos)
        # context['orfan_partidos'] = Partido.objects.filter(amba_zone=None)
        # context['total_orfan_partidos'] = Partido.objects.filter(
        #     amba_zone=None).count()
        return context


class ZoneUpdateView(
        UpdateAlertMixin, ContextMixin, LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    form_class = UpdateZoneForm
    template_name = "places/zone/edit.html"
    context = {'selected_tab': 'zone-tab'}

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Zone, id=id_)

    def form_valid(self, form):
        msg = f'La zona "{form.instance.name.title()}" ' +\
            'se actualizó correctamente'
        self.add_alert(msg=msg)
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('places:zone-detail', kwargs={'pk': self.object.pk})


@login_required(login_url='/login/')
def zone_delete(request, *args, **kwargs):

    zoneids = kwargs['zoneids'].split("-")

    delete_utility = DeleteObjectsUtil(
        model=Zone,
        model_ids=zoneids,
        order_by='name',
        request=request,
        selected_tab='zone-tab'
    )

    if request.method == 'POST':
        delete_utility.delete_objects()
        delete_utility.create_alert()
        return redirect('places:zone-list')

    if request.method == 'GET':
        context = delete_utility.get_context_data()

    return render(request, "places/zone/delete.html", context)
# ************* END FLEX *************
