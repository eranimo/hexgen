from unittest import TestCase
from hexgen.hex import Hex, HexSide
from hexgen.edge import Edge
from hexgen.grid import Grid

class TestEdge(TestCase):

    def setUp(self):
        hex_grid = []
        self.grid = Grid(hex_grid)
        h1 = Hex(self.grid, 0, 0, 1)
        h2 = Hex(self.grid, 0, 1, 11)
        h3 = Hex(self.grid, 0, 2, 23)

        h4 = Hex(self.grid, 1, 0, 5)
        h5 = Hex(self.grid, 1, 1, 15)
        h6 = Hex(self.grid, 1, 2, 33)

        h7 = Hex(self.grid, 2, 0, 32)
        h8 = Hex(self.grid, 2, 1, 36)
        h9 = Hex(self.grid, 2, 2, 36)
        self.grid.grid.append([h1, h2, h3])
        self.grid.grid.append([h4, h5, h6])
        self.grid.grid.append([h7, h8, h9])
        self.grid.calculate()
        self.h1 = self.grid.find_hex(0, 0)
        self.h4 = self.grid.find_hex(1, 0)
        self.h9 = self.grid.find_hex(2, 2)
        self.e1 = self.h1.edge_south_east
        self.e2 = self.h4.edge_north_west
        self.e3 = self.h9.edge_north_west

    def test_calculate(self):
        self.assertTrue(isinstance(self.e1, Edge), "e1 is not an Edge, calculate() "
                                                   "may not be working")

    def test_sides(self):
        self.assertTrue(self.e1.side == HexSide.south_east, "Edge has wrong HexSide enum")

    def test_init(self):
        self.assertTrue(self.e1.one == self.h1,
                        "'one' value for Hex 1 Edge 1 is not Hex 1, was {}".format(self.e1.one))
        self.assertTrue(self.e1.two == self.h4,
                        "'two' value for Hex 2 Edge 1 is not Hex 4, was {}".format(self.e1.two))

    def test_equality(self):
        """ Tests that the __eq__ function is working correctly """
        self.assertTrue(self.e1 == self.e1, "E1 equals E1")
        self.assertTrue(self.e1 == self.e2,
                        "Hex 1 Edge SE and Hex 4 Edge NW should be equal, was \n{}\n{}"
                        .format(self.e1, self.e2))
        self.assertFalse(self.e1 == self.e3, "Hex 1 Edge SE and Hex 9 Edge NW should not be equal")
