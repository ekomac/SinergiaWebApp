# Basic Python
import unidecode
from typing import List

# Django imports
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

# Projects utils
from utils.views import DeleteObjectsUtil, ContextMixin
from utils.forms import CheckPasswordForm
from utils.alerts.views import (
    SuccessfulUpdateAlertMixin,
    create_alert_and_redirect,
    update_alert_and_redirect
)

# Project apps
from account.models import Account
from places.models import Partido, Town, Zone
from places.forms import (
    UpdatePartidoForm,
    AddZoneForm,
    UpdateTownForm,
    UpdateZoneForm
)

TOWNS_PER_PAGE = 30
PARTIDOS_PER_PAGE = 20
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

NAME_ORDERING = {
    'name': 'name',
    'name_desc': '-name',
    None: 'name',
}


# ************************ PARTIDO ************************
@login_required(login_url='/login/')
def partidos_view(request, *args, **kwargs):
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

        partidos = get_partido_queryset(query, order_by)

        # Pagination
        page = request.GET.get('page', 1)
        partidos_paginator = Paginator(partidos, PARTIDOS_PER_PAGE)
        try:
            partidos = partidos_paginator.page(page)
        except PageNotAnInteger:
            partidos = partidos_paginator.page(PARTIDOS_PER_PAGE)
        except EmptyPage:
            partidos = partidos_paginator.page(partidos_paginator.num_pages)

        context['partidos'] = partidos
        context['totalPartidos'] = len(partidos)
        context['selected_tab'] = 'partido-tab'

    return render(request, "places/partido/list.html", context)


def get_partido_queryset(
        query: str = None, order_by_key: str = 'name') -> List[Partido]:
    """Get all partidos that match provided query, if any. If none is given,
    returns all partidos. Also, performs the query in the specified order.

    Args:
        query (str, optional): words to match the query. Defaults to empyt str.
        order_by_key (str, optional): to perform ordery by. Defaults to 'name'.

    Returns:
        List[Partido]: a list containing the partidos which match at least
        one query.
    """
    query = unidecode.unidecode(query) if query else ""
    return list(Partido.objects.filter(Q(name__icontains=query))
                .order_by(NAME_ORDERING[order_by_key]).distinct())


class PartidoDetailView(ContextMixin, LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = Partido
    template_name = "places/partido/detail.html"
    context = {'selected_tab': 'partido-tab'}


@login_required(login_url='/login/')
def edit_partido_view(request, pk, *args, **kwargs):

    print("func started")
    partido = get_object_or_404(Partido, pk=pk)
    print("partido is", partido)
    form = UpdatePartidoForm(instance=partido)
    print("form is", form)

    if request.method == 'POST':
        print("methos is POST")
        form = UpdatePartidoForm(request.POST or None, instance=partido)
        print("form is", form)

        if form.is_valid():
            print("form is valid")
            obj = form.save(commit=False)
            print("obj is", obj)
            author = Account.objects.filter(email=request.user.email).first()
            print("author is", author)
            obj.updated_by = author
            obj.save()
            partido = obj
            print("partido is", partido)
            msg = f'El partido "{obj.name.title()}" se actualizó correctamente'
            return update_alert_and_redirect(
                request, msg, 'places:partido-detail', obj.pk)

    context = {
        'form': form,
        'selected_tab': 'partido-tab',
    }
    return render(request, "places/partido/edit.html", context)


@login_required(login_url='/login/')
def bulk_edit_partidos_view(request, pk, *args, **kwargs):

    partido = get_object_or_404(Partido, pk=pk)
    form = UpdatePartidoForm(instance=partido)

    if request.method == 'POST':
        form = UpdateZoneForm(request.POST or None, instance=partido)

        if form.is_valid():
            obj = form.save(commit=False)
            author = Account.objects.filter(email=request.user.email).first()
            obj.updated_by = author
            obj.save()
            partido = obj
            msg = f'El partido "{obj.name.title()}" se actualizó correctamente'
            return update_alert_and_redirect(
                request, msg, 'places:partido-detail', obj.pk)

    context = {
        'form': form,
        'selected_tab': 'partido-tab',
    }
    return render(request, "places/partido/edit.html", context)


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
        query: str = None, order_by_key: str = 'partido') -> List[Town]:
    """Get all towns that match provided query, if any. If none is given,
    returns all towns. Also, performs the query in the specified order.

    Args:
        query (str, optional): words to match the query. Defaults to empyt str.
        order_by_key (str, optional): to perform ordery by.
        Defaults to 'partido'.

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
        SuccessfulUpdateAlertMixin,
        ContextMixin, LoginRequiredMixin, UpdateView):
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
        'partidosTotal': Partido.objects.count(),
    }

    form = AddZoneForm(request.POST or None)
    ids = request.POST.get('selected_partidos_ids', None)
    if form.is_valid():
        # Save the object after asigning the user who is updating
        obj = form.save(commit=False)
        author = Account.objects.filter(email=request.user.email).first()
        obj.updated_by = author
        obj.save()
        set_partido_ids(ids, obj)
        form = AddZoneForm()
        msg = f'La zona "{obj.name.title()}" se creó correctamente.'
        return create_alert_and_redirect(
            request, msg, 'places:zone-detail', obj.pk)

    context['form'] = form
    context['partidos_ids'] = ids

    return render(request, "places/zone/add.html", context)


def set_partido_ids(ids: str, obj: Zone) -> None:
    """Updates amba_zone attr for each Partido found for each id,
    if any id was given.

    Args:
        ids (str): contains ids of Partidos to update, in
        a "id1-id2-id3" format.
        obj (Zone): the one to set in every Partido as their amba_zone.
    """
    if ids:
        for id in ids.split("-"):
            partido = get_object_or_404(Partido, pk=id)
            partido.amba_zone = obj
            partido.save()


class ZoneDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = Zone
    template_name = "places/zone/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_tab'] = 'zone-tab'
        context['total_partidos'] = self.object.partido_set.count()
        context['partidos'] = self.object.partido_set.order_by('name').all()
        return context


@login_required(login_url='/login/')
def edit_zone_view(request, pk, *args, **kwargs):

    zone = get_object_or_404(Zone, pk=pk)
    form = UpdateZoneForm(instance=zone)

    if request.method == 'POST':
        form = UpdateZoneForm(request.POST or None, instance=zone)

        if form.is_valid():
            obj = form.save(commit=False)
            author = Account.objects.filter(email=request.user.email).first()
            obj.updated_by = author
            obj.save()
            zone = obj
            ids = request.POST.get('selected_partidos_ids', None)
            update_partido_ids(ids, obj)
            msg = f'La zona "{obj.name.title()}" se actualizó correctamente.'
            return update_alert_and_redirect(
                request, msg, 'places:zone-detail', obj.pk)

    context = {
        'form': form,
        'partidos': Partido.objects.all(),
        'partidosTotal': Partido.objects.count(),
        'partidos_ids': get_partidos_ids(zone),
        'selected_tab': 'zone-tab',
    }
    return render(request, "places/zone/edit.html", context)


def get_partidos_ids(zone: Zone, as_list: bool = False):
    ids = zone.partido_set.all()
    ids = [str(partido.id) for partido in ids] if ids else []
    if as_list:
        return ids
    if len(ids) > 0:
        return "-".join(ids)
    return ""


def update_partido_ids(new_ids: str, obj: Zone) -> None:
    """Updates amba_zone attr for each Partido found for each id,
    if any id was given.

    Args:
        ids (str): contains ids of Partidos to update, in
        a "id1-id2-id3" format.
        obj (Zone): the one to set in every Partido as their amba_zone.
    """
    previous_ids = get_partidos_ids(obj, as_list=True)
    new_ids = new_ids.split("-") if new_ids else []
    # Deattach zone from previous partidos if now not present
    for id in previous_ids:
        if id not in new_ids:
            partido = get_object_or_404(Partido, pk=id)
            partido.amba_zone = None
            partido.save()
    # Attach zone to partidos if not previously present
    for id in new_ids:
        if id not in previous_ids:
            partido = get_object_or_404(Partido, pk=id)
            partido.amba_zone = obj
            partido.save()

    # print("attempting to update")
    # if new_ids:
    #     print("ids is not None")
    #     new_ids = new_ids.split("-")
    #     print("ids", new_ids)
    #     previous_ids = get_partidos_ids(obj, as_list=True)
    #     print("previous ids", previous_ids)
    #     if previous_ids:
    #         print("previous ids is not None")
    #         for id in previous_ids:
    #             print("id", id, "en previous")
    #             if id not in new_ids:
    #                 print("id", id, "no está en ids:", new_ids)
    #                 partido = get_object_or_404(Partido, pk=id)
    #                 partido.amba_zone = None
    #                 partido.save()
    #     print("para cada id en ids")
    #     for id in new_ids:
    #         print("id", id, "en ids:", new_ids)
    #         partido = get_object_or_404(Partido, pk=id)
    #         partido.amba_zone = obj
    #         partido.save()


class ZoneUpdateView(
        SuccessfulUpdateAlertMixin,
        ContextMixin, LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    form_class = UpdateZoneForm
    template_name = "places/zone/edit.html"
    context = {'selected_tab': 'zone-tab', }

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

    context = {}
    if request.method == 'POST':
        form = CheckPasswordForm(request.POST or None,
                                 current_password=request.user.password)
        if form.is_valid():
            delete_utility.delete_objects()
            delete_utility.create_alert()
            return redirect('places:zone-list')
    else:  # Meaning is a GET request
        form = CheckPasswordForm()
    context = delete_utility.get_context_data()
    context['form'] = form
    # context['password_match'] = passwords_match

    return render(request, "places/zone/delete.html", context)
# ************* END FLEX *************
