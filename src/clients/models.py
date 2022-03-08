from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models


def upload_location(instance, filename):
    date = instance.date_created.strftime("%Y-%m-%d_%H-%M-%S")
    file_path = "contracts/{client_id}/{date}-{filename}".format(
        client_id=str(instance.id), date=date, filename=filename
    )
    return file_path


class Client(models.Model):

    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Creación")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Autor",
        blank=True,
        null=True,
        default=None,
        related_name="client_created_by",
    )
    name = models.CharField(
        verbose_name="Razón social / Nombre fantasía",
        max_length=100,
        blank=False,
        null=False,
        unique=True,
    )
    contact_name = models.CharField(
        verbose_name="Persona de contacto",
        max_length=50, blank=True, null=True
    )
    contact_phone = models.CharField(
        verbose_name="Número de teléfono", max_length=50, blank=True, null=True
    )
    contact_email = models.CharField(
        verbose_name="Email", max_length=50, blank=True, null=True
    )
    contract = models.FileField(
        upload_to=upload_location,
        blank=True,
        null=True,
        verbose_name="Contrato",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "jpg", "png", "jpeg", "doc", "docx"]
            )
        ],
    )

    @property
    def contract_url(self):
        if self.contract and hasattr(self.contract, "url"):
            return self.contract.url
        return None

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['name']


@receiver(post_delete, sender=Client)
def submission_delete(sender, instance, **kwargs):
    instance.contract.delete(False)


class Discount(models.Model):

    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Creación")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Autor",
        blank=True,
        null=True,
        default=None,
        related_name="discount_created_by",
    )
    amount = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name="Porcentaje",
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name="Cliente")
    partidos = models.ManyToManyField(
        "places.Partido", blank=True, verbose_name="Partidos"
    )
    is_for_flex = models.BooleanField(
        default=False, verbose_name="Es para envíos flex")

    def __str__(self) -> str:
        return "{a}% de descuento para {b} por {c} partidos".format(
            a=self.amount, b=self.client.name, c=self.partidos.count()
        )

    class Meta:
        verbose_name = "descuento"
        verbose_name_plural = "descuentos"
        ordering = ['amount']
