import re
from decimal import Decimal
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.forms import CheckPasswordForm

from utils.views import DeleteObjectsUtil
from .forms import (
    CreateDeliveryCodeForm,
    CreateFlexCodeForm,
    UpdateDeliveryCodeForm,
    UpdateFlexCodeForm,
    BaseBulkEditPercentageForm,
    # BaseBulkEditAmountForm,
)

from account.models import Account
from .models import DeliveryCode, FlexCode
from places.models import Town
from utils.alerts.views import (
    SuccessfulCreationAlertMixin,
    SuccessfulUpdateAlertMixin,
    update_alert_and_redirect
)


# ****************** MENSAJERIA ******************
@login_required(login_url='/login/')
def delivery_codes_view(request, *args, **kwargs):

    context = {}

    if request.method == 'GET':

        dcodes = DeliveryCode.objects.all().order_by('code')
        context['dcodes'] = dcodes
        context['totalCodes'] = len(dcodes)
        context['selected_tab'] = 'dprices-tab'

    return render(request, "prices/dcode-list.html", context)


class DeliveryCodeAddView(
        SuccessfulCreationAlertMixin, LoginRequiredMixin, CreateView):
    login_url = '/login/'
    template_name = "prices/add.html"
    form_class = CreateDeliveryCodeForm

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        self.add_alert(
            f'El código {form.instance.code} se creó correctamente.')
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prices:dcode-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super(DeliveryCodeAddView, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'dprices-tab'
        ctx['code_type'] = 'd'
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


class DeliveryCodeDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = DeliveryCode
    template_name = "prices/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_tab'] = 'dprices-tab'
        towns = Town.objects.filter(
            delivery_code=kwargs['object']).order_by('partido__name', 'name')
        context['towns'] = towns
        context['total_towns'] = len(towns)
        context['code_type'] = 'd'
        return context


class DeliveryCodeUpdateView(
        SuccessfulUpdateAlertMixin, LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    form_class = UpdateDeliveryCodeForm
    template_name = "prices/edit.html"

    def get_context_data(self, **kwargs):
        ctx = super(DeliveryCodeUpdateView, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'dprices-tab'
        ctx['code_type'] = 'd'
        return ctx

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(DeliveryCode, id=id_)

    def form_valid(self, form):
        self.add_alert(
            msg=f'El código {form.instance.code} se actualizó correctamente.',
        )
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prices:dcode-detail', kwargs={'pk': self.object.pk})


@login_required(login_url='/login/')
def delivery_code_bulk_update(request, **kwargs):
    pass


@login_required(login_url='/login/')
def delivery_code_delete(request, *args, **kwargs):

    dcodesids = kwargs['dcodeids'].split("-")

    delete_utility = DeleteObjectsUtil(
        model=DeliveryCode,
        model_ids=dcodesids,
        order_by='code',
        request=request,
        selected_tab='dprices-tab')

    if request.method == 'POST':
        delete_utility.delete_objects()
        delete_utility.create_alert()
        return redirect('prices:dcode-list')

    context = {}
    if request.method == 'GET':
        context = delete_utility.get_context_data()

    return render(request, "prices/delete.html", context)


# ****************** FLEX ******************
@login_required(login_url='/login/')
def flex_codes_view(request, *args, **kwargs):

    context = {}
    context['selected_tab'] = 'fprices-tab'

    if request.method == 'GET':

        fcodes = FlexCode.objects.all().order_by('code')
        context['fcodes'] = fcodes
        context['totalCodes'] = len(fcodes)
        context['selected_tab'] = 'fprices-tab'

    return render(request, "prices/fcode-list.html", context)


class FlexCodeAddView(
        SuccessfulCreationAlertMixin, LoginRequiredMixin, CreateView):
    login_url = '/login/'
    template_name = "prices/add.html"
    form_class = CreateFlexCodeForm

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        self.add_alert(
            msg=f'El código {form.instance.code} se creó correctamente.',
        )
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prices:fcode-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super(FlexCodeAddView, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'fprices-tab'
        ctx['code_type'] = 'f'
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


class FlexCodeDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = FlexCode
    template_name = "prices/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_tab'] = 'fprices-tab'
        towns = Town.objects.filter(
            flex_code=kwargs['object']).order_by('partido__name', 'name')
        context['towns'] = towns
        context['total_towns'] = len(towns)
        context['code_type'] = 'f'
        return context


class FlexCodeUpdateView(
        SuccessfulUpdateAlertMixin, LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    form_class = UpdateFlexCodeForm
    template_name = "prices/edit.html"

    def get_context_data(self, **kwargs):
        ctx = super(FlexCodeUpdateView, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'fprices-tab'
        ctx['code_type'] = 'f'
        return ctx

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(FlexCode, id=id_)

    def form_valid(self, form):
        self.add_alert(
            msg=f'El código {form.instance.code} se actualizó correctamente.',
        )
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prices:fcode-detail', kwargs={'pk': self.object.pk})


@login_required(login_url='/login/')
def flex_code_bulk_percentage_update(request, fcodeids):

    ids = fcodeids.split("-")
    fcodes = FlexCode.objects.filter(id__in=ids)

    update_form = BaseBulkEditPercentageForm()
    password_form = CheckPasswordForm()

    if request.method == 'POST':
        update_form = BaseBulkEditPercentageForm(request.POST or None)
        password_form = CheckPasswordForm(
            request.POST or None,
            current_password=request.user.password)

        if update_form.is_valid() and password_form.is_valid():
            percentage = update_form.cleaned_data['percentage']
            author = Account.objects.filter(email=request.user.email).first()
            names = []
            for fcode in fcodes:
                fcode.price = fcode.price + \
                    Decimal(Decimal(fcode.price) * Decimal(percentage) / 100)
                fcode.updated_by = author
                names.append(fcode.code)
            FlexCode.objects.bulk_update(fcodes, ['price', 'updated_by'])
            names = '", "'.join(names)
            msg = f'Los partidos "{names}" se actualizaron correctamente'
            return update_alert_and_redirect(
                request, msg, 'prices:fcode-list')

    context = {
        'update_form': update_form,
        'password_form': password_form,
        'code_type': 'f',
        'selected_tab': 'fprices-tab',
        'fcodes': fcodes,
        'fcodes_count': len(fcodes),
    }
    return render(request,
                  "prices/fcode-percentage-bulkedit.html",
                  context)


@login_required(login_url='/login/')
def flex_code_delete(request, *args, **kwargs):

    fcodesids = kwargs['fcodeids'].split("-")

    delete_utility = DeleteObjectsUtil(
        model=FlexCode,
        model_ids=fcodesids,
        order_by='code',
        request=request,
        selected_tab='fprices-tab'
    )

    if request.method == 'POST':
        delete_utility.delete_objects()
        delete_utility.create_alert()
        return redirect('prices:fcode-list')

    context = {}
    if request.method == 'GET':
        context = delete_utility.get_context_data()

    return render(request, "prices/delete.html", context)
# ************* END FLEX *************
