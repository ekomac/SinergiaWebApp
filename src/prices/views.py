from django.shortcuts import render
from .models import DeliveryCode, FlexCode
from django.views.generic.base import View
# from django.views.generic.detail import DetailView
# from django.views.generic.edit import CreateView
# from django.views.generic import ListView


class PricesContextMixin(View):

    def get_context_data(self, **kwargs):
        ctx = super(PricesContextMixin, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'prices-tab'
        return ctx


def codes_view(request, *args, **kwargs):

    context = {}
    context['selected_tab'] = 'prices-tab'

    if request.method == 'GET':

        context['dcodes'] = DeliveryCode.objects.all()
        context['fcodes'] = FlexCode.objects.all()

    return render(request, "prices/codes_list.html", context)
