import os
from django import forms
from django.conf import settings
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from account.models import Account
from clients.models import Client
from deposit.models import Deposit
from envios.bulkutil.exceptions import (
    InvalidExcelFileError, InvalidPdfFileError)
from envios.bulkutil.extractor import Extractor
from envios.models import BulkLoadEnvios
from envios.utils import bulk_create_envios

from places.models import Partido, Town
from prices.models import DeliveryCode, FlexCode


def extract_files_data(file):
    """
    Extract the data from the file and return it as a Dict[str, Any].
    """
    try:
        extractor = Extractor()
        result = extractor.get_shipments(file)['result']
        return [row.split(',') for row in result.split("\n")]
    except InvalidPdfFileError:
        raise forms.ValidationError("El PDF proporcionado no es\
            ni de MercadoLibre ni de TiendaNube")
    except InvalidExcelFileError:
        raise forms.ValidationError("El archivo de Excel proporcionada \
            no es válido.")


class HowToGetData:

    @classmethod
    def setData(cls):
        cls.user = Account.objects.create(
            email="juan.perez@gmail.com",
            username="juan.perez",
            is_admin=True,
            is_active=True,
            is_staff=True,
            can_distribute=True,
            is_superuser=False,
            has_access_denied=False,
            first_name="Juan",
            last_name="Pérez",
        )
        cls.fcode = FlexCode.objects.create(code='flex', price=1.0)
        cls.dcode = DeliveryCode.objects.create(
            code='delivery', price=1.0, max_5k_price=1.0,
            bulto_max_10k_price=1.5, bulto_max_20k_price=1.8,
            miniflete_price=1.9, tramite_price=2.0,)
        cls.partido = Partido.objects.create(name="SAN MIGUEL", is_amba=True)
        cls.town_bella_vista = Town.objects.create(
            name='BELLA VISTA', partido=cls.partido,
            delivery_code=cls.dcode, flex_code=cls.fcode)
        cls.town_san_miguel = Town.objects.create(
            name='SAN MIGUEL', partido=cls.partido,
            delivery_code=cls.dcode, flex_code=cls.fcode)
        cls.town_muniz = Town.objects.create(
            name='MUNIZ', partido=cls.partido,
            delivery_code=cls.dcode, flex_code=cls.fcode)
        cls._client = Client.objects.create(
            created_by=cls.user, name="Bulonera")
        cls.deposit = Deposit.objects.create(
            created_by=cls.user,
            client=cls._client,
            name="Bulonera San Miguel",
            address="Av. Dr. R. Balbín 123",
            town=cls.town_san_miguel)


class TestUtils1(HowToGetData, TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.setData()

    def test_01_file_extract(self):
        """Extract shipments from file"""
        with open(os.path.join(settings.BASE_DIR,
                               'envios/tests/sample_xlsx_1.xlsx'), 'rb') as f:
            self.file = SimpleUploadedFile(f.name, f.read())
            self.csv_result = extract_files_data(self.file)
            self.assertEqual(
                int(self.csv_result[1][4]), self.town_bella_vista.pk)
            self.assertEqual(int(self.csv_result[2][4]), self.town_muniz.pk)
            self.assertEqual(
                int(self.csv_result[3][4]), self.town_san_miguel.pk)


class TestUtils2(HowToGetData, TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.setData()
        with open(os.path.join(settings.BASE_DIR,
                               'envios/tests/sample_xlsx_1.xlsx'), 'rb') as f:
            cls.file = SimpleUploadedFile(f.name, f.read())
            cls.csv_result = extract_files_data(cls.file)

    def test_01_bulk_create(self):
        """Bulk create from file"""
        self.bulk_load = BulkLoadEnvios.objects.create(
            client=self._client, deposit=self.deposit,
            csv_result="\n".join([",".join(row) for row in self.csv_result]))
        envios, _ = bulk_create_envios(self.bulk_load)
        for envio in envios:
            self.assertEqual(envio.town.partido.name, 'SAN MIGUEL')
            self.assertIn(envio.town.name, [
                          'SAN MIGUEL', 'BELLA VISTA', 'MUNIZ'])
