# Python
import re
from decimal import Decimal
from typing import Any, Dict
from django.http import Http404, JsonResponse

# Django
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

# Project
from account.decorators import allowed_users, allowed_users_in_class_view
from account.models import Account
from clients.models import Discount
from places.utils import get_localidades_as_JSON, get_places_data_for_dcode


from utils.forms import CheckPasswordForm
from utils.views import CompleteListView, DeleteObjectsUtil
from utils.alerts.views import (
    SuccessfulCreationAlertMixin,
    SuccessfulUpdateAlertMixin,
    update_alert_and_redirect
)
from .forms import (
    BulkEditAmountForm,
    CreateDeliveryCodeForm,
    CreateFlexCodeForm,
    UpdateDeliveryCodeForm,
    UpdateFlexCodeForm,
    BulkEditPercentageForm,
)

from .models import DeliveryCode, FlexCode
from places.models import Partido, Town


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "Clients", ])
def cotizador_view(request):
    if request.method == 'GET':
        context = {}
        context['selected_tab'] = 'cotizador-tab'
        context['partidos'] = Partido.objects.all().order_by("name")
        context['places'] = get_localidades_as_JSON()
        return render(request, 'prices/cotizador.html', context)
    return Http404()


@login_required(login_url='/login/')
@allowed_users(roles=["Admins", "Clients", ])
def calcular_cotizacion_view(request):
    if request.method == 'GET':
        town_id = request.GET.get('town_id')
        town = get_object_or_404(Town, id=town_id)
        max5kg_amount = int(request.GET.get('max5kg', 0))
        max10kg_amount = int(request.GET.get('max10kg', 0))
        max20kg_amount = int(request.GET.get('max20kg', 0))
        miniflete_amount = int(request.GET.get('miniflete', 0))
        tramite_amount = int(request.GET.get('tramite', 0))
        result = 0
        result += town.delivery_code.max_5k_price * max5kg_amount
        result += town.delivery_code.bulto_max_10k_price * max10kg_amount
        result += town.delivery_code.bulto_max_20k_price * max20kg_amount
        result += town.delivery_code.miniflete_price * miniflete_amount
        result += town.delivery_code.tramite_price * tramite_amount

        if request.user.groups.filter(name='Clients').exists():
            print("es cliente")
            discount = Discount.objects.filter(
                client=request.user.client,
                is_for_flex=False,
                partidos__in=[town.partido]
            ).first()
            print(discount)

            # If discount exists, apply it to the total price
            if discount:
                discount = Decimal(discount.amount) / Decimal(100)
                total_discount = result * discount
                result = result - total_discount
                result = str(result) + " con el descuento de " + \
                    str(discount * 100) + "%"
        return JsonResponse({'result': result})
    return Http404()


class DeliveryCodeListView(CompleteListView, LoginRequiredMixin):
    template_name = 'prices/dcode_list.html'
    decoders = None
    model = DeliveryCode
    query_keywords = (
        'code__icontains',)
    selected_tab = 'dprices-tab'
    include_add_button = False

    @allowed_users_in_class_view(roles=["Admins", "Clients", ])
    def get(self, request):
        return super(DeliveryCodeListView, self).get(request)

    def queryset_map_callable(self, obj):
        return self.to_dict_with_extra_info(obj)

    def to_dict_with_extra_info(self, obj: DeliveryCode) -> Dict[str, Any]:
        dcode = get_places_data_for_dcode(dcode=obj)
        dcode['id'] = obj.id
        dcode['code'] = obj.code
        dcode['max_5k_price'] = obj.max_5k_price
        dcode['bulto_max_10k_price'] = obj.bulto_max_10k_price
        dcode['bulto_max_20k_price'] = obj.bulto_max_20k_price
        dcode['miniflete_price'] = obj.miniflete_price
        dcode['tramite_price'] = obj.tramite_price
        return dcode

    def get_context_data(self, **kwargs):
        context = super(DeliveryCodeListView, self).get_context_data(**kwargs)

        return context


class FlexCodeListView(CompleteListView, LoginRequiredMixin):
    template_name = 'prices/fcode_list.html'
    decoders = None
    model = FlexCode
    query_keywords = (
        'code__icontains',)
    selected_tab = 'fprices-tab'
    include_add_button = False

    def queryset_map_callable(self, obj: FlexCode):
        all_partidos = Partido.objects.filter(
            town__in=obj.town_set.all())
        sorted_partidos = all_partidos.order_by('name').distinct()
        only_names = [val.title()
                      for val in sorted_partidos.values_list(
            'name', flat=True)]
        return {
            'code': obj.code,
            'price': '{:.2f}'.format(obj.price),
            'partidos': set(only_names),
        }

    @ allowed_users_in_class_view(roles=["Admins", "Clients", ])
    def get(self, request):
        return super(FlexCodeListView, self).get(request)


# ****************** MENSAJERIA ******************
@ login_required(login_url='/login/')
@ allowed_users(roles="Admins")
def delivery_codes_view(request, *args, **kwargs):

    context = {}

    if request.method == 'GET':

        dcodes = DeliveryCode.objects.all().order_by('code')
        context['dcodes'] = dcodes
        context['totalCodes'] = len(dcodes)
        context['selected_tab'] = 'dprices-tab'

    return render(request, "prices/dcode-list2.html", context)


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

    @ allowed_users_in_class_view(roles="Admins")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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

    @ allowed_users_in_class_view(roles="Admins")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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

    @ allowed_users_in_class_view(roles="Admins")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@ login_required(login_url='/login/')
@ allowed_users(roles="Admins")
def delivery_code_bulk_fixed_update(request, dcodeids):

    ids = dcodeids.split("-")
    fcodes = DeliveryCode.objects.filter(id__in=ids)

    update_form = BulkEditAmountForm()
    password_form = CheckPasswordForm()

    if request.method == 'POST':
        update_form = BulkEditAmountForm(request.POST or None)
        password_form = CheckPasswordForm(
            request.POST or None,
            current_password=request.user.password)

        if update_form.is_valid() and password_form.is_valid():
            author = Account.objects.filter(email=request.user.email).first()
            names = []
            for fcode in fcodes:
                fcode.price = fcode.price + update_form.cleaned_data['amount']
                fcode.updated_by = author
                names.append(fcode.code)
            DeliveryCode.objects.bulk_update(fcodes, ['price', 'updated_by'])
            names = '", "'.join(names)
            msg = f'Los códigos de mensajería "{names}" \
                se actualizaron correctamente'
            return update_alert_and_redirect(
                request, msg, 'prices:dcode-list')

    context = {
        'update_form': update_form,
        'password_form': password_form,
        'code_type': 'f',
        'selected_tab': 'fprices-tab',
        'fcodes': fcodes,
        'fcodes_count': len(fcodes),
    }
    return render(request, "prices/fixed-bulk-edit.html", context)


@ login_required(login_url='/login/')
@ allowed_users(roles="Admins")
def delivery_code_bulk_percentage_update(request, dcodeids):

    ids = dcodeids.split("-")
    fcodes = DeliveryCode.objects.filter(id__in=ids)

    update_form = BulkEditPercentageForm()
    password_form = CheckPasswordForm()

    if request.method == 'POST':
        update_form = BulkEditPercentageForm(request.POST or None)
        password_form = CheckPasswordForm(
            request.POST or None,
            current_password=request.user.password)

        if update_form.is_valid() and password_form.is_valid():
            author = Account.objects.filter(email=request.user.email).first()
            names = []
            for fcode in fcodes:
                percentage = update_form.cleaned_data['percentage']
                fcode.price = fcode.price + \
                    Decimal(Decimal(fcode.price) * Decimal(percentage) / 100)
                fcode.updated_by = author
                names.append(fcode.code)
            DeliveryCode.objects.bulk_update(fcodes, ['price', 'updated_by'])
            names = '", "'.join(names)
            msg = f'Los códigos de mensajería "{names}" \
                se actualizaron correctamente'
            return update_alert_and_redirect(
                request, msg, 'prices:dcode-list')

    context = {
        'update_form': update_form,
        'password_form': password_form,
        'code_type': 'f',
        'selected_tab': 'fprices-tab',
        'fcodes': fcodes,
        'fcodes_count': len(fcodes),
    }
    return render(request, "prices/percentage-bulk-edit.html", context)


@ login_required(login_url='/login/')
@ allowed_users(roles="Admins")
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
@ login_required(login_url='/login/')
@ allowed_users(roles="Admins")
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

    @ allowed_users_in_class_view(roles="Admins")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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

    @ allowed_users_in_class_view(roles="Admins")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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

    @ allowed_users_in_class_view(roles="Admins")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@ login_required(login_url='/login/')
@ allowed_users(roles="Admins")
def flex_code_bulk_fixed_update(request, fcodeids):

    ids = fcodeids.split("-")
    fcodes = FlexCode.objects.filter(id__in=ids)

    update_form = BulkEditAmountForm()
    password_form = CheckPasswordForm()

    if request.method == 'POST':
        update_form = BulkEditAmountForm(request.POST or None)
        password_form = CheckPasswordForm(
            request.POST or None,
            current_password=request.user.password)

        if update_form.is_valid() and password_form.is_valid():
            author = Account.objects.filter(email=request.user.email).first()
            names = []
            for fcode in fcodes:
                fcode.price = fcode.price + update_form.cleaned_data['amount']
                fcode.updated_by = author
                names.append(fcode.code)
            FlexCode.objects.bulk_update(fcodes, ['price', 'updated_by'])
            names = '", "'.join(names)
            msg = f'Los códigos flex "{names}" se actualizaron correctamente'
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
    return render(request, "prices/fixed-bulk-edit.html", context)


@ login_required(login_url='/login/')
@ allowed_users(roles="Admins")
def flex_code_bulk_percentage_update(request, fcodeids):

    ids = fcodeids.split("-")
    fcodes = FlexCode.objects.filter(id__in=ids)

    update_form = BulkEditPercentageForm()
    password_form = CheckPasswordForm()

    if request.method == 'POST':
        update_form = BulkEditPercentageForm(request.POST or None)
        password_form = CheckPasswordForm(
            request.POST or None,
            current_password=request.user.password)

        if update_form.is_valid() and password_form.is_valid():
            author = Account.objects.filter(email=request.user.email).first()
            names = []
            for fcode in fcodes:
                percentage = update_form.cleaned_data['percentage']
                fcode.price = fcode.price + \
                    Decimal(Decimal(fcode.price) * Decimal(percentage) / 100)
                fcode.updated_by = author
                names.append(fcode.code)
            FlexCode.objects.bulk_update(fcodes, ['price', 'updated_by'])
            names = '", "'.join(names)
            msg = f'Los códigos flex "{names}" se actualizaron correctamente'
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
    return render(request, "prices/percentage-bulk-edit.html", context)


@ login_required(login_url='/login/')
@ allowed_users(roles="Admins")
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
