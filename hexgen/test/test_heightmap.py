from unittest import TestCase

from hexgen.mapgen import default_params
from hexgen.heightmap import Heightmap

class TestHeightmap(TestCase):

    def setUp(self):
        params = default_params
        self.size = 50
        params['size'] = self.size
        self.heightmap = Heightmap(params)

    def test_init(self):
        self.assertEqual(len(self.heightmap.grid), self.size, "Grid size is incorrect")

    def test_wrap(self):
        self.assertEqual(self.heightmap.grid[1][0], self.heightmap.grid[1][-1],
                         "Heightmap does not wrap horizontally")
        self.assertEqual(self.heightmap.grid[-1][1], self.heightmap.grid[-1][-2],
                         "Heightmap does not wrap vertically on the bottom")
