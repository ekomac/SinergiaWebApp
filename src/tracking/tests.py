from django.test import TestCase as DjangoTestCase
from unittest import TestCase


class TestTracking(TestCase):
    def test_withdraw(self):
        self.assertEqual(1, 1)
