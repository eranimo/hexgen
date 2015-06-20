from unittest import TestCase

from hexgen.util import latitude_to_number

class TestLatitudeToNumber(TestCase):

    def test_basic(self):
        self.assertEqual(latitude_to_number(0, 100), 50, "0°N is supposed to be the equator")
        self.assertEqual(latitude_to_number(90, 100), 0, "90°N is supposed to be the north pole")
        self.assertEqual(latitude_to_number(-90, 100), 100, "90°S is supposed to be the south pole")

    def test_tropics(self):
        self.assertEqual(latitude_to_number(45, 100), 25, "45°N is supposed to be the north tropics")
        self.assertEqual(latitude_to_number(-45, 100), 75, "45°S is supposed to be the south tropics")
