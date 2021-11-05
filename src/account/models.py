from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from simple_history.models import HistoricalRecords


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
    return f'account/{account_id}/dni-{account_id}'


def profile_pic_upload_location(instance, filename, *args, **kwargs):
    account_id = str(instance.id)
    return f'account/{account_id}/profile-{account_id}'


class Account(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(verbose_name="email",
                              max_length=100, unique=True)
    username = models.CharField(max_length=40, unique=True)
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
    history = HistoricalRecords()

    # USER INFO
    first_name = models.CharField(verbose_name="first name", max_length=30)
    last_name = models.CharField(verbose_name="last name", max_length=30)
    phone = models.CharField(verbose_name="phone",
                             max_length=20, blank=True, null=True)
    dni = models.CharField(verbose_name="dni", max_length=8,
                           unique=True, blank=True, null=True)
    address = models.CharField(
        verbose_name="address", max_length=100, blank=True, null=True)
    dni_img = models.ImageField(verbose_name='doc picture',
                                upload_to=doc_upload_location,
                                blank=True, null=True)

    # USER DOCUMENTATION
    # role (client
    # admin
    # employee)
    # drivers_license
    # criminal_record
    # vtv
    # insurance
    # vehicle_id
    # tax_doc
    # grose_income
    # is_collector
    # is_distributor
    # is_dealer
    # extra_doc_1
    # extra_doc_2
    # extra_doc_3

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
