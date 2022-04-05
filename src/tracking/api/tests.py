# from django.urls import reverse
# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from rest_framework.test import APITestCase
# from account.models import Account
# from clients.models import Client
# from deposit.models import Deposit
# from envios.models import Envio
# from places.models import Partido, Town
# from prices.models import DeliveryCode, FlexCode
# from tracking.models import TrackingMovement
# from utils import sample_data as samples


# class WithdrawWithMockDbTestCase(APITestCase):

#     reverse_to_app = None

#     def setUp(self):
#         self.superuser = Account(**samples.superuser)
#         self.superuser.save()
#         self.session_on = False
#         self.create_db()

#     def reset_db_session(self, **kwargs):
#         if self.session_on is False:
#             if hasattr(self, 'session_vars') and self.session_vars:
#                 for name, value in self.session_vars:
#                     if isinstance(value, (list, tuple, set)):
#                         items = []
#                         for item in value:
#                             items.append(getattr(self, item))
#                         setattr(self, name, items)
#                     else:
#                         setattr(self, name, getattr(self, value))
#             self.envio_1.deposit = self.deposit
#             self.envio_2.deposit = self.deposit
#             self.envio_3.deposit = self.deposit
#             self.envio_4.deposit = self.deposit
#             self.client.login(username=self.superuser.email,
#                               password='AMERICA123')
#             # self.superuser_token = Token.objects.create(user=self.superuser)
#             self.superuser_token = Token.objects.get(user__is_superuser=True)
#             self.client.credentials(
#                 HTTP_AUTHORIZATION='Token ' + self.superuser_token.key)
#             self.session_on = True

#     def create_db(self):
#         self.delivery_code = DeliveryCode(**samples.delivery_codes[0])
#         self.delivery_code.save()
#         self.flex_code = FlexCode(**samples.flex_codes[0])
#         self.flex_code.save()
#         self.partido = Partido(**samples.partidos[0])
#         self.partido.save()
#         self.town_1 = Town(**samples.towns[0])
#         self.town_1.partido = self.partido
#         self.town_1.flex_code = self.flex_code
#         self.town_1.delivery_code = self.delivery_code
#         self.town_1.save()
#         self.town_2 = Town(**samples.towns[1])
#         self.town_2.partido = self.partido
#         self.town_2.flex_code = self.flex_code
#         self.town_2.delivery_code = self.delivery_code
#         self.town_2.save()
#         self.carrier = Account(**samples.carriers[0])
#         self.carrier.save()
#         self._client = Client(**samples.clients[0])
#         self._client.save()
#         self.deposit = Deposit(**samples.deposits[0])
#         self.deposit.client = self._client
#         self.deposit.town = self.town_1
#         self.deposit.save()
#         self.envio_1 = Envio(**samples.envios[0])
#         self.envio_1.client = self._client
#         self.envio_1.created_by = self.superuser
#         self.envio_1.deposit = self.deposit
#         self.envio_1.town = self.town_1
#         self.envio_1.save()
#         self.envio_2 = Envio(**samples.envios[0])
#         self.envio_2.client = self._client
#         self.envio_2.created_by = self.superuser
#         self.envio_2.deposit = self.deposit
#         self.envio_2.town = self.town_1
#         self.envio_2.save()
#         self.envio_3 = Envio(**samples.envios[0])
#         self.envio_3.client = self._client
#         self.envio_3.created_by = self.superuser
#         self.envio_3.deposit = self.deposit
#         self.envio_3.town = self.town_2
#         self.envio_3.save()
#         self.envio_4 = Envio(**samples.envios[0])
#         self.envio_4.client = self._client
#         self.envio_4.created_by = self.superuser
#         self.envio_4.deposit = self.deposit
#         self.envio_4.town = self.town_2
#         self.envio_4.save()

#         self.tracking_movement = TrackingMovement(
#             created_by=self.superuser,
#             action=TrackingMovement.ACTION_ADDED_TO_SYSTEM,
#             result=TrackingMovement.RESULT_ADDED_TO_SYSTEM,
#             deposit=self.deposit
#         )
#         self.tracking_movement.save()
#         self.tracking_movement.envios.add(*[self.envio_1])

#     def post(self, data={}):
#         if self.reverse_to_app is None:
#             raise ValueError('reverse_to_app is not defined')
#         url = reverse(self.reverse_to_app)
#         return self.client.post(url, data, format='json')


# class WithdrawAllTestCase(WithdrawWithMockDbTestCase):

#     reverse_to_app = 'tracking:api-withdraw-all'

#     def test_login_not_authenticated(self):
#         response = self.post()
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertEqual(
#             response.data['detail'],
#             "Authentication credentials were not provided.")

#     def test_withdraw_all(self):
#         self.reset_db_session()
#         data = {
#             'deposit': self.deposit.id,
#             'carrier': self.carrier.id,
#         }
#         response = self.post(data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         last_movement = TrackingMovement.objects.last()
#         self.assertEqual(last_movement.action,
#                          TrackingMovement.ACTION_COLLECTION)
#         self.assertEqual(last_movement.result,
#                          TrackingMovement.RESULT_TRANSFERED)
#         # Check this movements has at least one envio
#         self.assertGreater(last_movement.envios.count(), 0)

#     def test_withdraw_all_with_no_carrier(self):
#         self.reset_db_session()
#         data = {
#             'deposit': self.deposit.id,
#         }
#         response = self.post(data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['response'],
#                          "Faltan datos de 'carrier'")

#     def test_withdraw_by_id_with_non_existent_carrier(self):
#         self.reset_db_session()
#         data = {
#             'carrier': 500,
#             'deposit': self.deposit.id,
#         }
#         response = self.post(data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['carrier'][0].code, "does_not_exist")

#     def test_withdraw_all_with_no_deposit(self):
#         self.reset_db_session()
#         data = {
#             'carrier': self.carrier.id,
#         }
#         response = self.post(data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['response'],
#                          "Faltan datos de 'deposit'")

#     def test_withdraw_by_id_with_non_existent_deposit(self):
#         self.reset_db_session()
#         data = {
#             'carrier': self.carrier.id,
#             'deposit': 500,
#         }
#         response = self.post(data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['deposit'][0].code, "does_not_exist")


# class WithdrawByIdTestCase(WithdrawWithMockDbTestCase):

#     reverse_to_app = 'tracking:api-withdraw-ids'

#     session_vars = [
#         ('envios', ['envio_1', 'envio_2']),
#     ]

#     def test_login_not_authenticated(self):
#         response = self.post()
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertEqual(
#             response.data['detail'],
#             "Authentication credentials were not provided.")

#     def test_withdraw_by_id_ok(self):
#         self.reset_db_session()
#         data = {
#             'deposit': self.deposit.id,
#             'carrier': self.carrier.id,
#             'envios_ids': [envio.id for envio in self.envios]
#         }
#         response = self.post(data)
#         last_movement = TrackingMovement.objects.last()
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(
#             last_movement.action, TrackingMovement.ACTION_COLLECTION)
#         self.assertEqual(last_movement.result,
#                          TrackingMovement.RESULT_TRANSFERED)
#         # Check this movements has at least one envio
#         self.assertGreater(last_movement.envios.count(), 0)
#         for envio in self.envios:
#             self.assertIn(envio, last_movement.envios.all())

#     def test_withdraw_by_id_with_no_carrier(self):
#         self.reset_db_session()
#         data = {
#             'deposit': self.deposit.id,
#             'envios_ids': [envio.id for envio in self.envios]
#         }
#         response = self.post(data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['response'],
#                          "Faltan datos de 'carrier'")

#     def test_withdraw_by_id_with_non_existent_carrier(self):
#         self.reset_db_session()
#         data = {
#             'carrier': 500,
#             'deposit': self.deposit.id,
#             'envios_ids': [envio.id for envio in self.envios]
#         }
#         response = self.post(data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['carrier'][0].code, "does_not_exist")

#     def test_withdraw_by_id_with_no_deposit(self):
#         self.reset_db_session()
#         data = {
#             'carrier': self.carrier.id,
#             'envios_ids': [envio.id for envio in self.envios]
#         }
#         response = self.post(data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['response'],
#                          "Faltan datos de 'deposit'")

#     def test_withdraw_by_id_with_non_existent_deposit(self):
#         self.reset_db_session()
#         data = {
#             'carrier': self.carrier.id,
#             'deposit': 500,
#             'envios_ids': [envio.id for envio in self.envios]
#         }
#         response = self.post(data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['deposit'][0].code, "does_not_exist")

#     def test_withdraw_by_id_with_no_ids(self):
#         self.reset_db_session()
#         data = {
#             'carrier': self.carrier.id,
#             'deposit': self.deposit.id,
#         }
#         response = self.post(data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(
#             response.data['envios_ids'], ["This field is required."])


# class WithdrawByFiltersWithTownTestCase(WithdrawWithMockDbTestCase):

#     reverse_to_app = 'tracking:api-withdraw-by-filter'

#     session_vars = [
#         ('towns', ['town_1', 'town_2']),
#     ]

#     def test_login_not_authenticated(self):
#         response = self.post()
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertEqual(
#             response.data['detail'],
#             "Authentication credentials were not provided.")

#     def test_withdraw_by_filter_w_town_ok(self):
#         self.reset_db_session()
#         data = {
#             'deposit': self.deposit.id,
#             'carrier': self.carrier.id,
#             'selected_ids': [town.id for town in self.towns],
#             'filter_by': 'town'
#         }
#         response = self.post(data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#         last_movement = TrackingMovement.objects.last()
#         self.assertEqual(
#             last_movement.action, TrackingMovement.ACTION_COLLECTION)
#         self.assertEqual(last_movement.result,
#                          TrackingMovement.RESULT_TRANSFERED)
#         # Check if there are envios in this movement which
#         # not correspond to the selected towns
#         self.assertEqual(
#             last_movement.envios.exclude(
#                 town__id__in=[town.id for town in self.towns]).count(), 0)
#         # Check this movements has at least one envio
#         self.assertGreater(last_movement.envios.count(), 0)
#         # Check this movements has at least one envio for the selected towns
#         self.assertGreater(
#             last_movement.envios.filter(
#                 town__id__in=[town.id for town in self.towns]).count(), 0)

#     # def test_withdraw_by_filter_with_town_no_carrier(self):
#     #     self.reset_db_session()
#     #     data = {
#     #         'deposit': self.deposit.id,
#     #         'selected_ids': [town.id for town in self.towns],
#     #         'filter_by': 'town'
#     #     }
#     #     response = self.post(data)
#     #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#     #     self.assertEqual(
#     #         response.data['response'], "Faltan datos de 'carrier'")

#     # def test_withdraw_by_filter_with_town_non_existent_carrier(self):
#     #     self.reset_db_session()
#     #     data = {
#     #         'carrier': 10,
#     #         'deposit': self.deposit.id,
#     #         'selected_ids': [town.id for town in self.towns],
#     #         'filter_by': 'town',
#     #     }
#     #     response = self.post(data)
#     #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#     #     self.assertEqual(response.data['carrier'][0].code, "does_not_exist")

#     # def test_withdraw_by_filter_with_town_no_deposit(self):
#     #     self.reset_db_session()
#     #     data = {
#     #         'carrier': self.carrier.id,
#     #         'selected_ids': [town.id for town in self.towns],
#     #         'filter_by': 'town',
#     #     }
#     #     response = self.post(data)
#     #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#     #     self.assertEqual(response.data['response'],
#     #                      "Faltan datos de 'deposit'")

#     # def test_withdraw_by_filter_with_town_non_existent_deposit(self):
#     #     self.reset_db_session()
#     #     data = {
#     #         'carrier': self.carrier.id,
#     #         'deposit': 10,
#     #         'selected_ids': [town.id for town in self.towns],
#     #         'filter_by': 'town',
#     #     }
#     #     response = self.post(data)
#     #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#     #     self.assertEqual(response.data['deposit'][0].code, "does_not_exist")

#     # def test_withdraw_by_filter_with_town_no_selected_ids(self):
#     #     self.reset_db_session()
#     #     data = {
#     #         'carrier': self.carrier.id,
#     #         'deposit': self.deposit.id,
#     #         'filter_by': 'town',
#     #     }
#     #     response = self.post(data)
#     #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#     #     self.assertEqual(
#     #         response.data['selected_ids'], ["This field is required."])

#     # def test_withdraw_by_filter_with_town_non_existent_towns(self):
#     #     self.reset_db_session()
#     #     data = {
#     #         'carrier': self.carrier.id,
#     #         'deposit': self.deposit.id,
#     #         'selected_ids': [10, 20],
#     #         'filter_by': 'town',
#     #     }
#     #     response = self.post(data)
#     #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#     #     self.assertEqual(
#     #         response.data['response'],
#     #         "Alguna de las localidades con ids [10, 20] no existe.")

#     # def test_withdraw_by_filter_with_town_no_filter_by(self):
#     #     self.reset_db_session()
#     #     data = {
#     #         'carrier': self.carrier.id,
#     #         'deposit': self.deposit.id,
#     #         'selected_ids': [town.id for town in self.towns],
#     #     }
#     #     response = self.post(data)
#     #     print(response.__dict__)
#     #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#     #     self.assertEqual(response.data['response'], "Falta el tipo filtro.")

#     def test_withdraw_by_filter_with_town_wrong_filter_by(self):
#         self.reset_db_session()
#         data = {
#             'carrier': "self.carrier.id",
#             'deposit': self.deposit.id,
#             'selected_ids': [town.id for town in self.towns],
#             'filter_by': 'wrong_filter',
#         }
#         response = self.post(data)
#         print(response.__dict__)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(
#             response.data['response'],
#             "Los filtros deben ser 'zone', 'partido' o 'town'.")
