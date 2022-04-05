# from rest_framework import status
# from rest_framework.reverse import reverse
# from account.models import Account
# from envios.models import Envio
# from places.models import Zone
# from utils.tests import MockDBAPITestCase


# class TownsTestCase(MockDBAPITestCase):
#     """
#     Tests querying for towns with the DRF API.

#     Args:
#         MockDBAPITestCase (APITestCase): Provides test database loading.
#     """

#     def test_001_get_towns_at_deposit(self):
#         url = reverse('places-api:towns-at-deposit', args=(self.deposit_1.id,))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code,
#                          status.HTTP_200_OK, "Status code is not 200")
#         self.assertEqual(
#             self.town_1.name.lower(),
#             response.data['results'][0]['name'].lower(),
#             "Name is not equal")
#         self.assertGreater(
#             len(response.data['results']), 0, "Didn't find any town")
#         self.assertEqual(
#             self.town_1.partido.name.lower(),
#             response.data['results'][0]['partido']['name'].lower(),
#             "Partido is not equal")

#     def test_002_get_towns_at_carrier(self):
#         print([envio for envio in Envio.objects.all()])
#         print([(user, user.full_name, user.id)
#               for user in Account.objects.all()])
#         print()
#         self.envio_1.carrier = self.carrier_1
#         self.envio_1.carrier.save()
#         self.envio_2.carrier = self.carrier_1
#         self.envio_2.carrier.save()
#         self.envio_3.carrier = self.carrier_1
#         self.envio_3.carrier.save()
#         self.envio_4.carrier = self.carrier_1
#         self.envio_4.carrier.save()
#         url = reverse('places-api:towns-at-carrier', args=(self.carrier_1.id,))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code,
#                          status.HTTP_200_OK, "Status code is not 200")
#         self.assertEqual(
#             self.town_1.name.lower(),
#             response.data['results'][0]['name'].lower(),
#             "Name is not equal")
#         self.assertGreater(
#             len(response.data['results']), 0, "Didn't find any town")
#         self.assertEqual(
#             self.town_1.partido.name.lower(),
#             response.data['results'][0]['partido']['name'].lower(),
#             "Partido is not equal")


# class PartidosTestCase(MockDBAPITestCase):
#     """
#     Tests querying for partidos with the DRF API.

#     Args:
#         MockDBAPITestCase (APITestCase): Provides test database loading.
#     """

#     def test_001_get_partidos_at_deposit(self):
#         url = reverse('places-api:partidos-at-deposit',
#                       args=(self.deposit_1.id,))
#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code,
#                          status.HTTP_200_OK, "Status code is not 200")
#         self.assertGreater(
#             len(response.data['results']), 0, "Didn't find any partido")
#         self.assertEqual(
#             self.partido_1.name.lower(),
#             response.data['results'][0]['name'].lower(),
#             "Partido's name is not equal")

#     def test_002_get_partidos_at_carrier(self):
#         print([envio for envio in Envio.objects.all()])
#         print([(user, user.full_name, user.id)
#               for user in Account.objects.all()])
#         self.envio_1.carrier = self.carrier_1
#         self.envio_1.carrier.save()
#         self.envio_2.carrier = self.carrier_1
#         self.envio_2.carrier.save()
#         self.envio_3.carrier = self.carrier_1
#         self.envio_3.carrier.save()
#         self.envio_4.carrier = self.carrier_1
#         self.envio_4.carrier.save()
#         url = reverse('places-api:partidos-at-carrier',
#                       args=(self.carrier_1.id,))
#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code,
#                          status.HTTP_200_OK, "Status code is not 200")
#         self.assertGreater(
#             len(response.data['results']), 0, "Didn't find any partido")
#         self.assertEqual(
#             self.partido_1.name.lower(),
#             response.data['results'][0]['name'].lower(),
#             "Partido's name is not equal")


# class ZonesTestCase(MockDBAPITestCase):
#     """
#     Tests querying for zones with the DRF API.

#     Args:
#         MockDBAPITestCase (APITestCase): Provides test database loading.
#     """

#     def test_001_get_zones_at_deposit(self):
#         url = reverse('places-api:zones-at-deposit', args=(self.deposit_1.id,))
#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code,
#                          status.HTTP_200_OK, "Status code is not 200")
#         self.assertGreater(
#             len(response.data['results']), 0, "Didn't find any zone")
#         self.assertEqual(
#             self.zone_1.name.lower(),
#             response.data['results'][0]['name'].lower(),
#             "Name is not equal")

#     def test_002_get_zones_at_carrier(self):
#         self.envio_1.carrier = self.carrier_1
#         self.envio_1.carrier.save()
#         self.envio_2.carrier = self.carrier_1
#         self.envio_2.carrier.save()
#         self.envio_3.carrier = self.carrier_1
#         self.envio_3.carrier.save()
#         self.envio_4.carrier = self.carrier_1
#         self.envio_4.carrier.save()
#         print(self.envio_4.carrier.id, "== ? ==", self.carrier_1.id)
#         print(self.envio_4.town.partido.zone)
#         print(Zone.objects.filter(
#             partido__town__destination__receiver__envio__carrier__id=self.carrier_1.id))
#         url = reverse('places-api:zones-at-carrier', args=(self.carrier_1.id,))
#         response = self.client.get(url, format='json')
#         print("REPSONSE", response.data)
#         self.assertEqual(response.status_code,
#                          status.HTTP_200_OK, "Status code is not 200")
#         self.assertGreater(
#             len(response.data['results']), 0, "Didn't find any zone")
#         self.assertEqual(
#             self.zone_1.name.lower(),
#             response.data['results'][0]['name'].lower(),
#             "Name is not equal")


# # class TownsAtTestCase(MockDBAPITestCase):
# #     """
# #     Tests querying for towns with the DRF API.

# #     Args:
# #         MockDBAPITestCase (APITestCase): Provides test database loading.
# #     """

# #     def test_001_get_towns_at_deposit(self):
# #         url = reverse('places-api:towns-at-deposit', args=(self.deposit_1.id,))
# #         response = self.client.get(url)
# #         self.assertEqual(response.status_code,
# #                          status.HTTP_200_OK, "Status code is not 200")
# #         self.assertEqual(
# #             self.town_1.name.lower(),
# #             response.data['results'][0]['name'].lower(),
# #             "Name is not equal")
# #         self.assertGreater(
# #             len(response.data['results']), 0, "Didn't find any town")
# #         self.assertEqual(
# #             self.town_1.partido.name.lower(),
# #             response.data['results'][0]['partido']['name'].lower(),
# #             "Partido is not equal")


# # class PartidosAtDepositTestCase(MockDBAPITestCase):
# #     """
# #     Tests querying for partidos with the DRF API.

# #     Args:
# #         MockDBAPITestCase (APITestCase): Provides test database loading.
# #     """

# #     def test_001_get_partidos_at_deposit(self):
# #         url = reverse('places-api:partidos-at-deposit',
# #                       args=(self.deposit_1.id,))
# #         response = self.client.get(url, format='json')
# #         self.assertEqual(response.status_code,
# #                          status.HTTP_200_OK, "Status code is not 200")
# #         self.assertGreater(
# #             len(response.data['results']), 0, "Didn't find any partido")
# #         self.assertEqual(
# #             self.partido_1.name.lower(),
# #             response.data['results'][0]['name'].lower(),
# #             "Partido's name is not equal")


# # class ZonesAtDepositTestCase(MockDBAPITestCase):
# #     """
# #     Tests querying for zones with the DRF API.

# #     Args:
# #         MockDBAPITestCase (APITestCase): Provides test database loading.
# #     """

# #     def test_001_get_zones_at_deposit(self):
# #         url = reverse('places-api:zones-at-deposit', args=(self.deposit_1.id,))
# #         response = self.client.get(url, format='json')
# #         self.assertEqual(response.status_code,
# #                          status.HTTP_200_OK, "Status code is not 200")
# #         self.assertGreater(
# #             len(response.data['results']), 0, "Didn't find any zone")
# #         self.assertEqual(
# #             self.zone_1.name.lower(),
# #             response.data['results'][0]['name'].lower(),
# #             "Name is not equal")
