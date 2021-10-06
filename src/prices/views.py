from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CreateDCodeForm, CreateFCodeForm
from .models import DeliveryCode, FlexCode
# from django.views.generic.edit import CreateView
# from django.views.generic import ListView


class PricesContextMixin(View):

    def get_context_data(self, **kwargs):
        ctx = super(PricesContextMixin, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'prices-tab'
        return ctx


class DPricesContextMixin(View):

    def get_context_data(self, **kwargs):
        ctx = super(DPricesContextMixin, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'dprices-tab'
        return ctx


class FPricesContextMixin(View):

    def get_context_data(self, **kwargs):
        ctx = super(FPricesContextMixin, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'fprices-tab'
        return ctx


def dcodes_view(request, *args, **kwargs):

    if not request.user.is_authenticated:
        return redirect('login')

    context = {}
    context['selected_tab'] = 'prices-tab'

    if request.method == 'GET':

        dcodes = DeliveryCode.objects.all()
        context['dcodes'] = dcodes
        context['totalCodes'] = len(dcodes)
        context['selected_tab'] = 'dprices-tab'

    return render(request, "prices/dcodes_list.html", context)


def fcodes_view(request, *args, **kwargs):

    if not request.user.is_authenticated:
        return redirect('login')

    context = {}
    context['selected_tab'] = 'fprices-tab'

    if request.method == 'GET':

        fcodes = FlexCode.objects.all()
        context['fcodes'] = fcodes
        context['totalCodes'] = len(fcodes)
        context['selected_tab'] = 'fprices-tab'

    return render(request, "prices/fcodes_list.html", context)


class AddDCodeView(DPricesContextMixin, LoginRequiredMixin, CreateView):
    model = DeliveryCode
    template_name = "prices/add_dcode.html"
    form_class = CreateDCodeForm

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prices:ddetail', kwargs={'pk': self.object.pk})


class AddFCodeView(FPricesContextMixin, LoginRequiredMixin, CreateView):
    model = FlexCode
    template_name = "prices/add_fcode.html"
    form_class = CreateFCodeForm

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prices:fdetail', kwargs={'pk': self.object.pk})


class DCodeDetailView(DPricesContextMixin, DetailView):
    model = DeliveryCode
    template_name = "prices/dcode_detail.html"


class FCodeDetailView(FPricesContextMixin, DetailView):
    model = FlexCode
    template_name = "prices/fcode_detail.html"
