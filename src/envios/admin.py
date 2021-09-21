from django.contrib import admin
from envios.models import Envio, Bolson, TrackingMovement


admin.site.register(Envio)
admin.site.register(Bolson)
admin.site.register(TrackingMovement)
