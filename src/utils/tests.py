from django.db.models.query import QuerySet
from django.db import models
from typing import Dict
from django.test import TestCase


class SampledDataTestCase(TestCase):

    SAMPLE_DATA = {}
    db_is_populated = False

    def setUp(self):
        if not self.db_is_populated:
            if not self.SAMPLE_DATA:
                raise ValueError('SAMPLE_DATA must be defined')
            create_from_sample_data(self.SAMPLE_DATA)
            self.db_is_populated = True


def create_from_sample_data(sample: dict):
    """Create instances objects from sample data.
    Sample data needs to be in the following format for this to work:

    {
        <Class>: {
            'values': (
                {'property': <value>, 'property2': <value>, ...},
                ...
            ),
            'relations': {
                <property name in parent class>: <related Class>,
                ...
            },
        },
        ...
    }

    Args:
        sample (dict): the data needed to create the instances.
    """

    def replace_class_with_instance(
        relations: Dict[str, models.Model]
    ) -> Dict[str, QuerySet]:
        """Replaces the class model with an instance.

        Args:
            relations (Dict[str, models.Model]): key-value pairs containg
            property names and related classes.

        Returns:
            Dict[str, QuerySet]: key-value pairs containg property names
            and related instances.
        """
        result = {}
        for key, value_class in relations.items():
            result[key] = value_class.objects.first()
        return result

    for model_name, dict_data in sample.items():
        relations_dict = {}
        if relations := dict_data.get('relations', None):
            relations_dict = replace_class_with_instance(relations)
        for values_dict in dict_data.get('values'):
            model_class = model_name
            values_dict.update(relations_dict)
            model_class.objects.create(**values_dict)
    return True


# # DJANGO
# from django.contrib.auth.models import Group

# # DJANGO REST FRAMEWORK
# from rest_framework.authtoken.models import Token
# from rest_framework.reverse import reverse
# from rest_framework.test import APITestCase

# # PROJECT
# from account.models import Account
# from clients.models import Client
# from deposit.models import Deposit
# from envios.models import Envio
# from places.models import Town, Partido, Zone
# from prices.models import DeliveryCode, FlexCode
# from tracking.models import TrackingMovement
# from utils import sample_data as samples


# class MockDBAPITestCase(APITestCase):

#     def setUp(self):
#         for element in dir(self):
#             if element.startswith('create_'):
#                 getattr(self, element)()
#         self.client.credentials(
#             HTTP_AUTHORIZATION='Token ' + self.superuser_token.key)

#     def create_01_groups(self):
#         self.group_admins = Group.objects.create(**samples.groups[0])
#         self.group_clients = Group.objects.create(**samples.groups[1])
#         self.group_employess_tier_1 = Group.objects.create(
# **samples.groups[2])
#         self.group_employess_tier_2 = Group.objects.create(
# **samples.groups[3])

#     def create_02_super_user(self):
#         if not Account.objects.filter(is_superuser=True).exists():
#             self.superuser = Account(**samples.superuser)
#             self.superuser.save()
#             self.superuser.groups.add(self.group_admins)
#             self.superuser.save()
#         else:
#             self.superuser = Account.objects.filter(
# is_superuser=True).first()

#     def create_03_token(self):
#         if Token.objects.filter(user__is_superuser=True).exists():
#             self.superuser_token = Token.objects.get(user__is_superuser=True)
#         else:
#             self.superuser_token = Token.objects.get(user__is_superuser=True)

#     def create_04_delivery_codes(self):
#         if not DeliveryCode.objects.filter(
#                 **samples.delivery_codes[0]).exists():
#             self.delivery_code = DeliveryCode(**samples.delivery_codes[0])
#             self.delivery_code.save()
#         else:
#             self.delivery_code = DeliveryCode.objects.filter(
#                 **samples.delivery_codes[0]).first()

#     def create_05_flex_codes(self):
#         if not FlexCode.objects.filter(**samples.flex_codes[0]).exists():
#             self.flex_code = FlexCode(**samples.flex_codes[0])
#             self.flex_code.save()
#         else:
#             self.flex_code = FlexCode.objects.filter(
#                 **samples.flex_codes[0]).first()

#     def create_06_zones(self):
#         if not Zone.objects.filter(**samples.zones[0]).exists():
#             self.zone_1 = Zone(**samples.zones[0])
#             self.zone_1.save()
#         else:
#             self.zone_1 = Zone.objects.filter(**samples.zones[0]).first()

#     def create_07_partidos(self):
#         if not Partido.objects.filter(**samples.partidos[0]).exists():
#             self.partido_1 = Partido(**samples.partidos[0])
#             self.partido_1.zone = self.zone_1
#             self.partido_1.save()
#         else:
#             self.partido_1 = Partido.objects.filter(
#                 **samples.partidos[0]).first()

#     def create_08_towns(self):
#         if not Town.objects.filter(**samples.towns[0]).exists():
#             self.town_1 = Town(**samples.towns[0])
#             self.town_1.partido = self.partido_1
#             self.town_1.flex_code = self.flex_code
#             self.town_1.delivery_code = self.delivery_code
#             self.town_1.save()
#         else:
#             self.town_1 = Town.objects.filter(**samples.towns[0]).first()

#         if not Town.objects.filter(**samples.towns[1]).exists():
#             self.town_2 = Town(**samples.towns[1])
#             self.town_2.partido = self.partido_1
#             self.town_2.flex_code = self.flex_code
#             self.town_2.delivery_code = self.delivery_code
#             self.town_2.save()
#         else:
#             self.town_2 = Town.objects.filter(**samples.towns[1]).first()

#     def create_09_carriers(self):
#         if not Account.objects.filter(**samples.carriers[0]).exists():
#             self.carrier_1 = Account(**samples.carriers[0])
#             self.carrier_1.save()
#             self.carrier_1.groups.add(self.group_employess_tier_1)
#             self.carrier_1.save()
#         else:
#             self.carrier_1 = Account.objects.filter(
#                 **samples.carriers[0]).first()
#         if not Account.objects.filter(**samples.carriers[1]).exists():
#             self.carrier_2 = Account(**samples.carriers[1])
#             self.carrier_2.save()
#             self.carrier_2.groups.add(self.group_employess_tier_2)
#             self.carrier_2.save()
#         else:
#             self.carrier_2 = Account.objects.filter(
#                 **samples.carriers[1]).first()

#         if not Account.objects.filter(**samples.carriers[2]).exists():
#             self.carrier_3 = Account(**samples.carriers[2])
#             self.carrier_3.save()
#             self.carrier_3.groups.add(self.group_employess_tier_2)
#             self.carrier_3.save()
#         else:
#             self.carrier_3 = Account.objects.filter(
#                 **samples.carriers[2]).first()

#     def create_10_clients(self):
#         if not Client.objects.filter(**samples.clients[0]).exists():
#             self.client_1 = Client(**samples.clients[0])
#             self.client_1.save()
#         else:
#             self.client_1 = Client.objects.filter(
#                 **samples.clients[0]).first()

#     def create_11_clients_accounts(self):
#         if not Account.objects.filter(
# **samples.clients_accounts[0]).exists():
#             self.client_account_1 = Account(**samples.clients_accounts[0])
#             self.client_account_1.save()
#             self.client_account_1.groups.add(self.group_clients)
#             self.client_account_1.save()
#         else:
#             self.client_account_1 = Account.objects.filter(
#                 **samples.clients_accounts[0]).first()

#     def create_12_deposits(self):
#         if not Deposit.objects.filter(**samples.deposits[0]).exists():
#             self.deposit_1 = Deposit(**samples.deposits[0])
#             self.deposit_1.client = self.client_1
#             self.deposit_1.town = self.town_1
#             self.deposit_1.save()
#         else:
#             self.deposit_1 = Deposit.objects.filter(
#                 **samples.deposits[0]).first()

#         if not Deposit.objects.filter(**samples.deposits[1]).exists():
#             self.deposit_2 = Deposit(**samples.deposits[1])
#             self.deposit_2.client = self.client_1
#             self.deposit_2.town = self.town_1
#             self.deposit_2.save()
#         else:
#             self.deposit_2 = Deposit.objects.filter(
#                 **samples.deposits[1]).first()

#     def create_13_envios(self):
#         for i, envio_sample in enumerate(samples.envios):
#             num = str(i + 1)
#             if not Envio.objects.filter(**envio_sample).exists():
#                 setattr(self, 'envio_' + num, Envio(**envio_sample))
#                 getattr(self, 'envio_' + num).client = self.client_1
#                 getattr(self, 'envio_' + num).created_by = self.superuser
#                 if i < 5:
#                     getattr(self, 'envio_' + num).deposit = self.deposit_1
#                 getattr(self, 'envio_' + num).town = self.town_1
#                 getattr(self, 'envio_' + num).save()
#             else:
#                 setattr(self, 'envio_' + num, Envio.objects.filter(
#                     **envio_sample).first())

#     def create_14_tracking_movements(self):
#         self.tracking_movement = TrackingMovement(
#             created_by=self.superuser,
#             action=TrackingMovement.ACTION_ADDED_TO_SYSTEM,
#             result=TrackingMovement.RESULT_ADDED_TO_SYSTEM,
#             deposit=self.deposit_1
#         )
#         self.tracking_movement.save()
#         self.tracking_movement.envios.add(*[self.envio_1])

#     @property
#     def url(self):
#         if self.reverse_to_app is None:
#             raise ValueError('reverse_to_app is not defined')
#         if self.reverse_to_app_args is None:
#             return reverse(self.reverse_to_app)
#         else:
#             return reverse(
# self.reverse_to_app, args=self.reverse_to_app_args)

#     def post(self, data={}):
#         return self.client.post(self.url, data, format='json')

#     def get(self):
#         return self.client.get(self.url, format='json')


# # class BaseMockDBTestCase(APITestCase):

# #     def setUp(self):
# #         for element in dir(self):
# #             if element.startswith('create_'):
# #                 getattr(self, element)()

# #     def create_01_groups(self):
# #         self.group_admins = Group.objects.create(**samples.groups[0])
# #         self.group_clients = Group.objects.create(**samples.groups[1])
# #         self.group_employess_tier_1 = Group.objects.create(
# #                                           **samples.groups[2])
# #         self.group_employess_tier_2 = Group.objects.create(
# #                                           **samples.groups[3])

# #     def create_02_super_user(self):
# #         self.superuser = Account(**samples.superuser)
# #         self.superuser.save()
# #         self.superuser.groups.add(self.group_admins)
# #         self.superuser.save()

# #     def create_03_token(self):
# #         self.superuser_token = Token.objects.get(user__is_superuser=True)

# #     def create_04_delivery_codes(self):
# #         self.delivery_code = DeliveryCode(**samples.delivery_codes[0])
# #         self.delivery_code.save()

# #     def create_05_flex_codes(self):
# #         self.flex_code = FlexCode(**samples.flex_codes[0])
# #         self.flex_code.save()

# #     def create_06_zones(self):
# #         self.zone = Zone(**samples.zones[0])
# #         self.zone.save()

# #     def create_07_partidos(self):
# #         self.partido = Partido(**samples.partidos[0])
# #         self.partido.zone = self.zone
# #         self.partido.save()

# #     def create_08_towns(self):
# #         self.town_1 = Town(**samples.towns[0])
# #         self.town_1.partido = self.partido
# #         self.town_1.flex_code = self.flex_code
# #         self.town_1.delivery_code = self.delivery_code
# #         self.town_1.save()
# #         self.town_2 = Town(**samples.towns[1])
# #         self.town_2.partido = self.partido
# #         self.town_2.flex_code = self.flex_code
# #         self.town_2.delivery_code = self.delivery_code
# #         self.town_2.save()

# #     def create_09_carriers(self):
# #         self.carrier_1 = Account(**samples.carriers[0])
# #         self.carrier_1.save()
# #         self.carrier_1.groups.add(self.group_employess_tier_1)
# #         self.carrier_1.save()
# #         self.carrier_2 = Account(**samples.carriers[1])
# #         self.carrier_2.save()
# #         self.carrier_2.groups.add(self.group_employess_tier_2)
# #         self.carrier_2.save()
# #         self.carrier_3 = Account(**samples.carriers[2])
# #         self.carrier_3.save()
# #         self.carrier_3.groups.add(self.group_employess_tier_2)
# #         self.carrier_3.save()

# #     def create_10_clients(self):
# #         self.client_1 = Client(**samples.clients[0])
# #         self.client_1.save()

# #     def create_11_clients_accounts(self):
# #         self.client_account = Account(**samples.clients_accounts[0])
# #         self.client_account.client = self.client_1
# #         self.client_account.save()
# #         self.client_account.groups.add(self.group_clients)
# #         self.client_account.save()

# #     def create_12_deposits(self):
# #         self.deposit_1 = Deposit(**samples.deposits[0])
# #         self.deposit_1.client = self.client_1
# #         self.deposit_1.town = self.town_1
# #         self.deposit_1.save()
# #         self.deposit_2 = Deposit(**samples.deposits[1])
# #         self.deposit_2.town = self.town_1
# #         self.deposit_2.save()

# #     def create_13_envios(self):
# #         for i, envio_sample in enumerate(samples.envios):
# #             num = str(i + 1).zfill(2)
# #             setattr(self, 'envio_' + num, Envio(**envio_sample))
# #             getattr(self, 'envio_' + num).client = self.client_1
# #             getattr(self, 'envio_' + num).created_by = self.superuser
# #             if i < 5:
# #                 getattr(self, 'envio_' + num).deposit = self.deposit_1
# #             getattr(self, 'envio_' + num).town = self.town_1
# #             getattr(self, 'envio_' + num).save()

# #     def create_14_tracking_movements(self):
# #         self.tracking_movement = TrackingMovement(
# #             created_by=self.superuser,
# #             action=TrackingMovement.ACTION_ADDED_TO_SYSTEM,
# #             result=TrackingMovement.RESULT_ADDED_TO_SYSTEM,
# #             deposit=self.deposit_1
# #         )
# #         self.tracking_movement.save()
# #         self.tracking_movement.envios.add(*[self.envio_1])


# # class BaseAuthorizationTestCase(APITestCase):
# #     """
# #     Test case for the authorization of the API
# #     """

# #     reverse_urls_apps = None

# #     def authorize(self):
# #         self.token = Token(user=self.superuser)
# #         self.token.save()
# #         self.client.credentials(
# HTTP_AUTHORIZATION='Token ' + self.token.key)

# #     def test_1_no_authorization(self):
# #         """
# #         Simple test to check if the authorization is working.
# #         """
# #         if isinstance(self.reverse_urls_apps, (tuple, list)):
# #             for app in self.reverse_urls_apps:
# #                 if isinstance(app, (tuple, list)):
# #                     url_app, url_args = app
# #                     if isinstance(url_args, list):
# #                         url_args = tuple(url_args)
# #                     self.assertEqual(
# #                         self.client.get(
# #                             reverse(url_app, args=url_args),
# #                             format="json").status_code,
# #                         status.HTTP_401_UNAUTHORIZED
# #                     )
# #                 elif isinstance(app, str):
# #                     self.assertEqual(
# #                         self.client.get(
# #                             reverse(app), format="json").status_code,
# #                         status.HTTP_401_UNAUTHORIZED
# #                     )

# #     def test_2_authorization(self):
# #         """
# #         Simple test to check if the authorization is working.
# #         """
# #         self.authorize()
# #         if isinstance(self.reverse_urls_apps, (tuple, list)):
# #             self.token = Token.objects.get(user=self.superuser)
# #             self.client.credentials(
# #                 HTTP_AUTHORIZATION='Token ' + self.token.key)
# #             for app in self.reverse_urls_apps:
# #                 if isinstance(app, (tuple, list)):
# #                     url_app, url_args = app
# #                     if isinstance(url_args, list):
# #                         url_args = tuple(url_args)
# #                     self.assertNotEqual(
# #                         self.client.get(
# #                             reverse(url_app, args=url_args),
# #                             format="json").status_code,
# #                         status.HTTP_401_UNAUTHORIZED
# #                     )
# #                 elif isinstance(app, str):
# #                     self.assertNotEqual(
# #                         self.client.get(
# #                             reverse(app), format="json").status_code,
# #                         status.HTTP_401_UNAUTHORIZED
# #                     )


# # class BaseAuthorizationWithDBTestCase(BaseMockDBTestCase):
# #     """
# #     Test case for the authorization of the API
# #     """

# #     reverse_urls_apps = None

# #     def authorize(self):
# #         self.token = Token(user=self.superuser)
# #         self.token.save()
# #         self.client.credentials(
# HTTP_AUTHORIZATION='Token ' + self.token.key)

# #     def test_1_no_authorization(self):
# #         """
# #         Simple test to check if the authorization is working.
# #         """
# #         if isinstance(self.reverse_urls_apps, (tuple, list)):
# #             for app in self.reverse_urls_apps:
# #                 if isinstance(app, (tuple, list)):
# #                     url_app, url_args = app
# #                     if isinstance(url_args, list):
# #                         url_args = tuple(url_args)
# #                     self.assertEqual(
# #                         self.client.get(
# #                             reverse(url_app, args=url_args),
# #                             format="json").status_code,
# #                         status.HTTP_401_UNAUTHORIZED
# #                     )
# #                 elif isinstance(app, str):
# #                     self.assertEqual(
# #                         self.client.get(
# #                             reverse(app), format="json").status_code,
# #                         status.HTTP_401_UNAUTHORIZED
# #                     )

# #     def test_2_authorization(self):
# #         """
# #         Simple test to check if the authorization is working.
# #         """
# #         if isinstance(self.reverse_urls_apps, (tuple, list)):
# #             self.token = Token.objects.get(user=self.superuser)
# #             self.client.credentials(
# #                 HTTP_AUTHORIZATION='Token ' + self.token.key)
# #             for app in self.reverse_urls_apps:
# #                 if isinstance(app, (tuple, list)):
# #                     url_app, url_args = app
# #                     if isinstance(url_args, list):
# #                         url_args = tuple(url_args)
# #                     self.assertNotEqual(
# #                         self.client.get(
# #                             reverse(url_app, args=url_args),
# #                             format="json").status_code,
# #                         status.HTTP_401_UNAUTHORIZED
# #                     )
# #                 elif isinstance(app, str):
# #                     self.assertNotEqual(
# #                         self.client.get(
# #                             reverse(app), format="json").status_code,
# #                         status.HTTP_401_UNAUTHORIZED
# #                     )
