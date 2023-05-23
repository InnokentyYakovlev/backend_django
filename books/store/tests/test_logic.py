from django.test import TestCase

from store.logic import operations


class LogicTestCase(TestCase):
    def test_plus(self):
        result = operations(6, 13, '+')
        self.assertEqual(19, result)

    def test_minus(self):
        result = operations(12, 2, '-')
        self.assertEqual(10, result)

    def test_multiply(self):
        result = operations(2, 4, '*')
        self.assertEqual(8, result)
