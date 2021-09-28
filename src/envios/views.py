from .models import Envio
from django.views.generic.edit import CreateView
from django.views.generic import ListView


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


class EnvioContextMixin(object):

    def get_context_data(self, **kwargs):
        ctx = super(EnvioCreate, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'shipments-tab'
        return ctx


def download_qr_code_label(request):
    pass


class EnvioCreate(EnvioContextMixin, CreateView):

    template_name = "envios/create_envio_admin.html"
    model = Envio
    fields = ['detail', 'client', 'recipient_name', 'recipient_doc',
              'recipient_phone', 'recipient_address',
              'recipient_entrances', 'recipient_town',
              'recipient_zipcode', 'recipient_charge', 'max_delivery_date',
              'is_flex', 'flex_id', 'delivery_schedule', ]
    context = {'hola': 'hola'}

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super(EnvioCreate, self).get_context_data(**kwargs)
        ctx['selected_tab'] = 'shipments-tab'
        return ctx


class EnviosList(ListView):
    model = Envio
    template_name = "envios/envio_list.html"
