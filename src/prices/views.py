import re
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    CreateDeliveryCodeForm,
    CreateFlexCodeForm,
    UpdateDeliveryCodeForm,
    UpdateFlexCodeForm,
)
from .models import DeliveryCode, FlexCode
from places.models import Town
from datetime import datetime
from alerts.alert import ToastAlert
from alerts.views import CreateAlertMixin


# ****************** MENSAJERIA ******************
def delivery_codes_view(request, *args, **kwargs):

    if not request.user.is_authenticated:
        return redirect('login')

    context = {}
    context['selected_tab'] = 'prices-tab'

    if request.method == 'GET':

        dcodes = DeliveryCode.objects.all().order_by('code')
        context['dcodes'] = dcodes
        context['totalCodes'] = len(dcodes)
        context['selected_tab'] = 'dprices-tab'

    return render(request, "prices/dcode/list.html", context)


class DPricesContextMixin(View):

    def get_context_data(self, **kwargs):
        ctx = super(DPricesContextMixin, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'dprices-tab'
        return ctx


class DeliveryCodeAddView(CreateAlertMixin, LoginRequiredMixin, CreateView):
    login_url = '/login/'
    template_name = "prices/dcode/add.html"
    form_class = CreateDeliveryCodeForm

    def form_valid(self, form):
        self.add_alert(
            topic='create',
            status='success',
            title='Creación correcta',
            msg=f'El código {form.instance.code} se creó correctamente.',
        )
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prices:dcode-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super(DeliveryCodeAddView, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'dprices-tab'
        # Intend to pass a suggestion code name to the view
        try:
            # Get last code name, from querying the database
            # with code param in descending order
            last_code_num = DeliveryCode.objects.all().order_by(
                '-code')[:1].get().code
            # Look for a number in the string
            result = re.search(r'\d.*', last_code_num)[0]
            # If result has something
            if result != '':
                # Make it an int, then adding 1
                result = int(result)+1
                # Fill the number with zeros
                result = f'{result}'.zfill(2)
                # Pass it to context
                ctx['name_suggestion'] = 'M' + result
        # If no Flex Code exists, pass to template the base suggestion
        except DeliveryCode.DoesNotExist:
            ctx['name_suggestion'] = 'M01'
        return ctx


class DeliveryCodeDetailView(DPricesContextMixin, DetailView):

    model = DeliveryCode
    template_name = "prices/dcode/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_tab'] = 'dprices-tab'
        towns = Town.objects.filter(
            delivery_code=kwargs['object']).order_by('partido__name', 'name')
        context['towns'] = towns
        context['total_towns'] = len(towns)
        return context


class DeliveryCodeUpdateView(
        CreateAlertMixin, DPricesContextMixin, LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    form_class = UpdateDeliveryCodeForm
    template_name = "prices/fcode/edit.html"

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(FlexCode, id=id_)

    def form_valid(self, form):
        self.add_alert(
            topic='create',
            status='success',
            title='Creación correcta',
            msg=f'El código {form.instance.code} se actualizó correctamente.',
        )
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prices:ddetail', kwargs={'pk': self.object.pk})


def delivery_code_confirm_delete(request, *args, **kwargs):

    if not request.user.is_authenticated:
        return redirect('login')

    context = {}

    if request.method == 'GET':
        dcodesids = kwargs['dcodeids'].split("-")
        dcodes = DeliveryCode.objects.filter(pk__in=dcodesids)
        context['dcodes'] = dcodes
        total_count = len(dcodes)
        context['total_count'] = total_count
        if total_count == 1:
            context['obj'] = dcodes[0]
        context['what_to_delete'] = str(
            total_count) + ' códigos de mensajería general'
        context['what_to_delete'] = str(
            total_count) + ' códigos de mensajería general'

    return render(request, "prices/confirm_ddelete.html", context)


# ****************** FLEX ******************
def flex_codes_view(request, *args, **kwargs):

    if not request.user.is_authenticated:
        return redirect('login')

    context = {}
    context['selected_tab'] = 'fprices-tab'

    if request.method == 'GET':

        fcodes = FlexCode.objects.all().order_by('code')
        context['fcodes'] = fcodes
        context['totalCodes'] = len(fcodes)
        context['selected_tab'] = 'fprices-tab'

    return render(request, "prices/fcode/list.html", context)


class FPricesContextMixin(View):

    def get_context_data(self, **kwargs):
        ctx = super(FPricesContextMixin, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'fprices-tab'
        return ctx


class FlexCodeAddView(CreateAlertMixin, LoginRequiredMixin, CreateView):
    login_url = '/login/'
    template_name = "prices/fcode/add.html"
    form_class = CreateFlexCodeForm

    def form_valid(self, form):
        self.add_alert(
            topic='create',
            status='success',
            title='Creación correcta',
            msg=f'El código {form.instance.code} se creó correctamente.',
        )
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prices:fcode-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super(FlexCodeAddView, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'fprices-tab'
        # Intend to pass a suggestion code name to the view
        try:
            # Get last code name, from querying the database
            # with code param in descending order
            last_code_num = FlexCode.objects.all().order_by(
                '-code')[:1].get().code
            # Look for a number in the string
            result = re.search(r'\d.*', last_code_num)[0]
            # If result has something
            if result != '':
                # Make it an int, then adding 1
                result = int(result)+1
                # Fill the number with zeros
                result = f'{result}'.zfill(2)
                # Pass it to context
                ctx['name_suggestion'] = 'F' + result
        # If no Flex Code exists, pass to template the base suggestion
        except FlexCode.DoesNotExist:
            ctx['name_suggestion'] = 'F01'
        return ctx


class FlexCodeDetailView(FPricesContextMixin, DetailView):
    model = FlexCode
    template_name = "prices/fcode/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_tab'] = 'fprices-tab'
        towns = Town.objects.filter(
            flex_code=kwargs['object']).order_by('partido__name', 'name')
        context['towns'] = towns
        context['total_towns'] = len(towns)
        return context


class FlexCodeUpdateView(
        CreateAlertMixin, FPricesContextMixin, LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    form_class = UpdateFlexCodeForm
    template_name = "prices/fcode/edit.html"

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(FlexCode, id=id_)

    def form_valid(self, form):
        self.add_alert(
            topic='create',
            status='success',
            title='Creación correcta',
            msg=f'El código {form.instance.code} se actualizó correctamente.',
        )
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prices:fcode-detail', kwargs={'pk': self.object.pk})


def flex_code_confirm_delete(request, *args, **kwargs):

    if not request.user.is_authenticated:
        return redirect('login')

    context = {}

    fcodesids = kwargs['fcodeids'].split("-")
    fcodes = FlexCode.objects.filter(pk__in=fcodesids)

    if request.method == 'GET':
        context['fcodes'] = fcodes
        total_count = len(fcodes)
        context['total_count'] = total_count
        context['selected_tab'] = 'fprices-tab'
        what = ' códigos de flex'
        if total_count == 1:
            what = ' código de flex'
            context['obj'] = fcodes[0]
        context['what_to_delete'] = str(total_count) + what

    if request.method == 'POST':
        fcodes_names = [fcode.code for fcode in fcodes]
        fcodes.delete()

        alerts = request.session.get('alerts', [])
        first_part = 'El código de flex "'
        last_part = '" se eliminó correctamente'

        if len(fcodes_names) > 1:
            first_part = 'Los códigos de flex "'
            last_part = '" se eliminaron correctamente.'

        message = first_part + ", ".join(fcodes_names) + last_part
        now = datetime.now()
        alert = ToastAlert(
            'delete',
            'success',
            'Eliminación correcta',
            message,
            now)
        alerts.append(alert.get_as_dict())
        request.session['alerts'] = alerts
        return redirect('prices:fcode-list')

    return render(request, "prices/confirm_fdelete.html", context)
# ************* END FLEX *************
