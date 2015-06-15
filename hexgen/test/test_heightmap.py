from unittest import TestCase

from hexgen import default_params
from hexgen.heightmap import Heightmap

class TestHeightmap(TestCase):

    def setUp(self):
        params = default_params
        params['size'] = 50
        self.heightmap = Heightmap(default_params)

    def test_size(self):
        self.assertTrue(len(self.heightmap.grid) == 2500, "Grid size is incorrect")
