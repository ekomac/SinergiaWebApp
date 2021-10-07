from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from places.models import Town


class TownDetailView(DetailView):
    model = Town
    template_name = "places/town_detail.html"


def towns_view(request, *args, **kwargs):

    if not request.user.is_authenticated:
        return redirect('login')

    context = {}
    context['selected_tab'] = 'fprices-tab'

    if request.method == 'GET':
        context['towns'] = Town.objects.all()
        context['selected_tab'] = 'places-tab'

    return render(request, "places/towns_list.html", context)
