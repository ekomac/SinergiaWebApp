from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from places.models import Town

# ************************ TOWN ************************


@login_required(login_url='/login/')
def towns_view(request, *args, **kwargs):

    context = {}
    context['selected_tab'] = 'fprices-tab'

    if request.method == 'GET':
        context['towns'] = Town.objects.all()
        context['selected_tab'] = 'places-tab'

    return render(request, "places/towns_list.html", context)


class TownDetailView(LoginRequiredMixin, DetailView):
    model = Town
    template_name = "places/town_detail.html"


# ************************ PARTIDO ************************


# ************************ ZONE ************************
