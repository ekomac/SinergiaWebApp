from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

import json

from envios.forms import CreateEnvioForm
from places.models import Partido, Town
from .models import Envio
from account.models import Account


# def create_envio_view(request):

#     user = request.user
#     if not user.is_authenticated:
#         return redirect('login')

#     context = {}

#     if request.method == "POST":
#         form = CreateEnvioForm(request.POST or None, request.FILES or None)
#         if form.is_valid():
#             obj = form.save()
#             author = Account.objects.filter(email=user.email)
#             obj.author = author
#             obj.save()
#             form = CreateEnvioForm()

#     context['form'] = form

#     return render(request, "envios/create_envio_admin.html", context)


class EnvioContextMixin(View):

    def get_context_data(self, **kwargs):
        ctx = super(EnvioContextMixin, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'shipments-tab'
        return ctx


class EnvioDetailView(EnvioContextMixin, DetailView):
    model = Envio


def download_qr_code_label(request):
    pass


class EnvioCreate(LoginRequiredMixin, CreateView):

    login_url = '/login/'
    template_name = "envios/create.html"
    form_class = CreateEnvioForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(EnvioCreate, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'shipments-tab'
        ctx['partidos'] = Partido.objects.all()
        ctx['places'] = get_localidades_as_JSON()
        return ctx

    def get_success_url(self):
        return reverse('envios:detail', kwargs={'pk': self.object.pk})


def get_localidades_as_JSON():
    query = Town.objects.all().order_by('name')
    mapped = list(map(map_town_to_dict, query))
    return json.dumps(mapped)


def map_town_to_dict(town):
    return {
        'id': town.id,
        'name': town.name.title(),
        'partido_id': town.partido.id,
    }


def create_envio_view(request):

    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    form = CreateEnvioForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        created_by = Account.objects.filter(email=user.email).first()
        obj.created_by = created_by
        obj.save()
        form = CreateEnvioForm()

    context['form'] = form

    return render(request, "envios/create.html", context)


class EnviosList(EnvioContextMixin, ListView):
    model = Envio
    template_name = "envios/list.html"


def update_envio(request):
    return render(request, 'envios/update.html', {})


def delete_envio(request):
    return render(request, 'envios/delete.html', {})
