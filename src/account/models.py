from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.conf import settings
from rest_framework.authtoken.models import Token


from clients.models import Client


class MyAccountManager(BaseUserManager):

    def create_user(self, email,
                    username, password, first_name, last_name):
        validations = [
            (email, 'un correo electrónico'),
            (username, 'un nombre de usuario'),
            (first_name, 'uno o más nombres'),
            (last_name, 'uno o más apellidos'), ]

        # VALIDATE REQUIRE USER FIELDS
        for param, spec in validations:
            if not param:
                raise ValueError(f'Los usuarios deben tener {spec}.')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email,
                         username, password, first_name, last_name):

        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


def doc_upload_location(instance, filename, *args, **kwargs):
    account_id = str(instance.id)
    return f'account/{account_id}/dni/{instance.dni}'


def driver_licence_upload_location(instance, filename):
    account_id = str(instance.id)
    return f'account/{account_id}/driver-licence/{filename}'


def criminal_record_upload_location(instance, filename):
    account_id = str(instance.id)
    return f'account/{account_id}/criminal-record/{filename}'


def vtv_upload_location(instance, filename):
    account_id = str(instance.id)
    return f'account/{account_id}/vtv/{filename}'


def insurance_upload_location(instance, filename):
    account_id = str(instance.id)
    return f'account/{account_id}/insurance/{filename}'


def profile_pic_upload_location(instance, filename, *args, **kwargs):
    account_id = str(instance.id)
    return f'account/{account_id}/profile-{account_id}'


class Account(AbstractBaseUser, PermissionsMixin):

    ROLES = (
        ('admin', 'Administrador'),
        ('client', 'Cliente'),
        ('level_1', 'Nivel 1'),
        ('level_2', 'Nivel 2'),
    )

    VEHICLES = (
        ('car', 'Automóvil'),
        ('motorcycle', 'Motocicleta'),
        ('truck', 'Camión'),
        ('van', 'Camioneta'),
        ('other', 'Otro'),
    )

    email = models.EmailField(verbose_name="email",
                              max_length=100, unique=True, null=False)
    username = models.CharField(max_length=40, unique=True, null=False)
    date_joined = models.DateTimeField(
        verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    can_distribute = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    profile_picture = models.ImageField(verbose_name="profile picture",
                                        upload_to=profile_pic_upload_location,
                                        blank=True, null=True)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, null=True, blank=True,
        related_name="client_user_account")

    # USER INFO
    first_name = models.CharField(verbose_name="first name", max_length=30)
    last_name = models.CharField(verbose_name="last name", max_length=30)
    date_of_birth = models.DateField(
        verbose_name="Fecha de nacimiento", null=True, blank=True)
    phone = models.CharField(verbose_name="phone",
                             max_length=20, blank=True, null=True)
    dni = models.CharField(verbose_name="dni", max_length=8,
                           unique=True, blank=True, null=True)
    address = models.CharField(
        verbose_name="address", max_length=100, blank=True, null=True)
    dni_img = models.ImageField(
        verbose_name='doc picture', upload_to=doc_upload_location, blank=True,
        null=True)
    # USER DOCUMENTATION
    role = models.CharField(verbose_name="Rol", max_length=9,
                            choices=ROLES, default='level_2')
    driver_license = models.FileField(
        verbose_name="Licencia de conducir",
        upload_to=driver_licence_upload_location, blank=True, null=True)
    criminal_record = models.FileField(
        verbose_name="Antecedentes penales",
        upload_to=criminal_record_upload_location, blank=True, null=True)
    vtv = models.FileField(
        verbose_name="VTV", upload_to=vtv_upload_location, blank=True,
        null=True)
    insurance = models.FileField(
        verbose_name="Seguro", upload_to=insurance_upload_location, blank=True,
        null=True)
    vehicle_type = models.CharField(
        verbose_name="Tipo de vehículo", max_length=10, blank=True, null=True,
        choices=VEHICLES)
    vehicle_id = models.CharField(
        verbose_name="Patente", max_length=10, blank=True, null=True)

    has_to_reset_password = models.BooleanField(
        default=False, verbose_name="¿Tiene que resetear la contraseña?")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    @property
    def full_name_formal(self):
        return self.last_name + ', ' + self.first_name

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def reset_password(self, password: str = None):
        self.has_to_reset_password = True
        self.save()

    @property
    def docs(self):
        docs = []
        if self.dni_img:
            docs.append("dni")
        if self.driver_license:
            docs.append("licencia de conducir")
        if self.criminal_record:
            docs.append("antecedentes penales")
        if self.vtv:
            docs.append("vtv")
        if self.insurance:
            docs.append("seguro")
        return ", ".join(docs)

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
        ordering = ['is_active', '-username']


@receiver(post_delete, sender=Account)
def submission_delete(sender, instance, **kwargs):
    instance.dni_img.delete(False)
    instance.driver_license.delete(False)
    instance.criminal_record.delete(False)
    instance.vtv.delete(False)
    instance.insurance.delete(False)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
