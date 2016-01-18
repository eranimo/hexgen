from enum import Enum
import uuid


class Edge:
    def __init__(self, side, one, two, up, down):
        """
            One and Two are Hexes on both sides.
            Up is the Hex upslope of the edge and Down is the Hex downslope
        """
        self.side = side
        self.one = one
        self.two = two
        self.up = up
        self.down = down
        self.delta = self.up.altitude - self.down.altitude
        self.id = uuid.uuid4()

        self.is_river = False

    def __repr__(self):
        return "<Edge Side: {}, One: {}, Two: {}, " \
               "Down: {}, delta: {}, direction: {}>".format(self.side, self.one, self.two, self.down, self.delta, self.direction)

    @property
    def is_coast(self):
        return self.one.is_water and self.two.is_land or \
               self.one.is_land and self.two.is_water

    @property
    def direction(self):
        if self.one.x == self.two.x:
            if self.down.x < self.one.x:
                return EdgeDirection.north
            else:
                return EdgeDirection.south
        else:
            if self.down == self.one.hex_east:
                if self.up == self.one.hex_north_west:
                    return EdgeDirection.south_east
                elif self.up == self.one.hex_south_west:
                    return EdgeDirection.north_east
            elif self.down == self.one.hex_west:
                if self.up == self.one.hex_north_east:
                    return EdgeDirection.south_west
                elif self.up == self.one.hex_south_east:
                    return EdgeDirection.north_west
            elif self.down == self.one.hex_north_west:
                return EdgeDirection.north_west
            elif self.down == self.one.hex_north_east:
                return EdgeDirection.north_east
            elif self.down == self.one.hex_south_west:
                return EdgeDirection.south_west
            elif self.down == self.one.hex_south_east:
                return EdgeDirection.south_east

    def __eq__(self, other):
        """
        :param other: Edge
        :return: True if both edges are equal to each other
        Eg: A Hex's south-east is equal to the bottom-left's north-west
        """
        return other.one == self.two or (self.one == other.one and self.two == other.two)

from hexgen.hex import HexSide

from hexgen.enums import EdgeDirection
