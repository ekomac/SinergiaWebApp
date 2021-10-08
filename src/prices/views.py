import re
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    CreateDCodeForm,
    CreateFCodeForm,
    UpdateFCodeForm
)
from .models import DeliveryCode, FlexCode
from places.models import Town
from datetime import datetime
from alerts.alert import ToastAlert
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

        dcodes = DeliveryCode.objects.all().order_by('code')
        context['dcodes'] = dcodes
        context['totalCodes'] = len(dcodes)
        context['selected_tab'] = 'dprices-tab'

    return render(request, "prices/dcode/list.html", context)


def fcodes_view(request, *args, **kwargs):

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


class AddDCodeView(DPricesContextMixin, LoginRequiredMixin, CreateView):
    model = DeliveryCode
    template_name = "prices/dcode/add.html"
    form_class = CreateDCodeForm

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prices:ddetail', kwargs={'pk': self.object.pk})


class AddFCodeView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    template_name = "prices/fcode/add.html"
    form_class = CreateFCodeForm

    def form_valid(self, form):
        self.__add_alert(form.instance.code)
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prices:fdetail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super(AddFCodeView, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'dprices-tab'
        # Intend to pass a suggestion code name to de view
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

    def __add_alert(self, name):
        """Adds an alert to request's session indicating the create action"""
        # Gets current alerts
        alerts = self.request.session.get('alerts', [])
        # Creates the message
        msg = f'El código {name} se creó correctamente.'
        # Get current time
        now = datetime.now()
        # Create the alert
        alert = ToastAlert(
            'create',
            'success',
            'Creación correcta',
            msg,
            now)
        # Append it to already existing ones
        alerts.append(alert.get_as_dict())
        # Set them back to request's session
        self.request.session['alerts'] = alerts
        return


class DCodeDetailView(DPricesContextMixin, DetailView):
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


class FCodeDetailView(FPricesContextMixin, DetailView):
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


class DCodeUpdateView(DPricesContextMixin, LoginRequiredMixin, UpdateView):
    pass


class FCodeUpdateView(FPricesContextMixin, LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    form_class = UpdateFCodeForm
    template_name = "prices/fcode/edit.html"

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(FlexCode, id=id_)

    def form_valid(self, form):
        self.__add_alert(form.instance.code)
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prices:fdetail', kwargs={'pk': self.object.pk})

    def __add_alert(self, name):
        """Adds an alert to request's session indicating the update action"""
        # Gets current alerts
        alerts = self.request.session.get('alerts', [])
        # Creates the message
        msg = f'El código {name} se actualizó correctamente.'
        # Get current time
        now = datetime.now()
        # Create the alert
        alert = ToastAlert(
            'update',
            'success',
            'Edición correcta',
            msg,
            now)
        # Append it to already existing ones
        alerts.append(alert.get_as_dict())
        # Set them back to request's session
        self.request.session['alerts'] = alerts
        return


def confirm_delete_dcode(request, *args, **kwargs):

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


def confirm_delete_fcode(request, *args, **kwargs):

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
        return redirect('prices:flist')

    return render(request, "prices/confirm_fdelete.html", context)
