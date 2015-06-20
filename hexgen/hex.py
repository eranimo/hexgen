import math
import random
from enum import Enum

from hexgen.constants import *
from hexgen.enums import Biome, MapType, HexType, HexFeature, HexSide, Zones
from hexgen.util import blend_colors, lighten, randomize_color, latitude_to_number


class Hex:
    def __init__(self, grid, x, y, altitude):
        self.x = x
        self.y = y
        self.altitude = altitude
        self.grid = grid

        self.edge_east = None
        self.edge_west = None
        self.edge_north_east = None
        self.edge_south_east = None
        self.edge_north_west = None
        self.edge_south_west = None

        self.distance = 0
        self.moisture = 0

        self.territory = None
        self.marked = False # marked by the grouping algorithm

        self.bubble_cache = dict()

        self.features = set()

        self.resource = None

        # instance of a sea
        self.sea = None

        if self.temperature <= -12 and self.is_water:
            self.features.add(HexFeature.glacier)

    def has_feature(self, feature):
        """
        Does this hex have this feature
        :param feature: HexFeature
        :return:
        """
        return feature in self.features

    def add_feature(self, feature):
        """
        Adds a feature
        :param feature: HexFeature
        :return: None
        """
        self.features.add(feature)

    def remove_feature(self, feature):
        """
        Removes a feature
        :param feature: HexFeature
        :return: None
        """
        self.features.remove(feature)

    @property
    def is_owned(self):
        return self.territory is not None

    @property
    def pressure(self):
        """ Returns a season dict that represents the pressure in mPa in summer and winter """

        # return {
        #     "summer": summer,
        #     "winter": winter
        # }

    @property
    def latitude_ratio(self):
        ratio = self.x / self.grid.size
        if ratio < 0.5:
            ratio /= 0.5
        else:
            ratio = (1 - ratio) / 0.5
        return ratio

    @property
    def latitude(self):
        """ Hex's current Latitude. Negative is south, positive is north """
        ratio = self.x / self.grid.size
        if ratio < 0.5: # north
            return (1 - ratio / 0.5) * 90
        else: # south
            return ((ratio ) / 0.5) * -90 + 90

    @property
    def zone(self):
        axial_tilt = abs(self.grid.params.get('axial_tilt'))

        # northern polar zone
        northern_polar_zone = 90 - axial_tilt
        southern_polar_zone = -(90 - axial_tilt)
        northern_tropic_zone = axial_tilt
        southern_tropic_zone = -axial_tilt
        northern_temperate = axial_tilt + (axial_tilt / 2)
        southern_temperate = -(axial_tilt + (axial_tilt / 2))

        if northern_polar_zone < self.latitude <= 90:
            return Zones.arctic_circle
        elif northern_temperate < self.latitude <= northern_polar_zone:
            return Zones.northern_temperate
        elif northern_tropic_zone < self.latitude <= northern_temperate:
            return Zones.northern_subtropics
        elif 0 < self.latitude <= northern_tropic_zone:
            return Zones.northern_tropics
        elif southern_tropic_zone < self.latitude <= 0:
            return Zones.southern_tropics
        elif southern_temperate < self.latitude <= southern_tropic_zone:
            return Zones.southern_subtropics
        elif southern_polar_zone < self.latitude <= southern_temperate:
            return Zones.southern_temperate
        elif -90 < self.latitude <= southern_polar_zone:
            return Zones.antarctic_circle

    @property
    def temperature(self):
        """
        Computes the temperature of this hex. Takes into account the latitude (x-coord) and
        the altitude (higher is colder)
        :return: number
        """
        # import ipdb; ipdb.set_trace()
        ratio = self.latitude_ratio
        avg_temp = self.grid.params.get('avg_temp')
        volitility = round(self.grid.params.get('axial_tilt') / 2)
        base_temp = self.grid.params.get('base_temp')
        min_temp = max(avg_temp - volitility, base_temp)
        # global avg temperature should be around ratio 0.4 and 0.6

        # part1 includes latitude only
        part1 = (abs(min_temp) + (avg_temp + volitility)) * ratio + min_temp
        #print(base_temp, avg_temp, volitility, min_temp, ratio, part1)
        #       43         73          16         57

        # part2 includes altitude
        factor = 7
        if self.is_water:
            factor = 8
        part2 = abs(self.altitude - self.grid.sealevel) / factor
        return round(part1, 2) - round(part2, 2)

    @property
    def biome(self):
        """
        Computes the biome
        :return: Biome
        """
        map_type = self.grid.params.get('map_type')
        if map_type is MapType.barren: # barren
            if self.grid.params.get('pressure') < 0.003: # trace atmosphere
                return Biome.barren
            else: # small atmosphere
                # TODO: determine where to put ice caps based on atmospheric compounds
                if self in self.grid.coldest_hexes and self.temperature < 0:
                    return Biome.barren_ice_caps
                elif self.moisture > 5 or self.has_feature(HexFeature.lake):
                    return Biome.barren_wet
                else:
                    return Biome.barren_dusty

        elif map_type is MapType.terran:
            temp = self.temperature
            rain = self.moisture
            if temp <= -10:
                return Biome.arctic
            elif 5 < rain and temp <= 0:
                return Biome.alpine_tundra
            elif 0 <= rain <= 5 and temp <= 0:
                return Biome.tundra
            elif 5 < rain and 0 < temp <= 7:
                return Biome.boreal_forest
            elif 0 <= rain <= 2.5 and 0 < temp <= 20:
                return Biome.grasslands
            elif 2.5 < rain <= 5 and 0 < temp <= 20:
                return Biome.shrubland
            elif 0 <= rain <= 5 and 20 < temp:
                return Biome.desert
            elif 5 < rain <= 10 and 7 < temp <= 20:
                return Biome.savanna
            elif 10 < rain <= 20 and 7 < temp <= 20:
                return Biome.temperate_forest
            elif 20 < rain and 7 < temp <= 20:
                return Biome.temperate_rainforest
            elif 5 < rain <= 20 and 20 < temp:
                return Biome.tropical_forest
            elif 20 < rain and 20 < temp:
                return Biome.tropical_rainforest

            raise Exception("Biome invalid Rainfall: {}, Temperature: {}".format(rain, temp))

        elif map_type is MapType.volcanic:
            if self.altitude < 60:
                return Biome.volcanic_liquid
            elif self.has_feature(HexFeature.lava_flow):
                return Biome.volcanic_molten_river
            else:
                return Biome.volcanic_solid

        return Biome.lifeless

    @property
    def max_size(self):
        return len(self.grid.grid) - 1

    @property
    def map_surrounding(self):
        """
        Returns the surrounding hexes without wrapping about the map
        :return: list of Hex
        """
        # east
        sur = []
        if self.y != self.max_size:
            sur.append(self.grid.find_hex(self.x, self.y + 1))
        # west
        if self.y != 0:
            sur.append(self.grid.find_hex(self.x, self.y - 1))
        # north west
        if self.x != 0 and self.y != 0:
            if self.x % 2 == 0:  # even
                sur.append(self.grid.find_hex(self.x - 1, self.y - 1))
            else:
                sur.append(self.grid.find_hex(self.x - 1, self.y))
        # north east
        if self.x != 0 and self.y != self.max_size:
            if self.x % 2 == 0:  # even
                sur.append(self.grid.find_hex(self.x - 1, self.y))
            else:
                sur.append(self.grid.find_hex(self.x - 1, self.y + 1))
        # south west
        if self.x != self.max_size and self.y != 0:
            if self.x % 2 == 0:  # even
                sur.append(self.grid.find_hex(self.x + 1, self.y - 1))
            else:
                sur.append(self.grid.find_hex(self.x + 1, self.y))
        # south east
        if self.x != self.max_size and self.y != self.max_size:
            if self.x % 2 == 0:  # even
                sur.append(self.grid.find_hex(self.x + 1, self.y))
            else:
                sur.append(self.grid.find_hex(self.x + 1, self.y + 1))
        return sur


    @property
    def hex_east(self):
        """ Returns the hex to the East or None if end of map"""
        if self.y == self.max_size:
            return self.grid.find_hex(self.x, 0)
        else:
            return self.grid.find_hex(self.x, self.y + 1)

    @property
    def hex_west(self):
        """ Returns the hex to the West or None if end of map"""
        if self.y == 0:
            return self.grid.find_hex(self.x, self.max_size)
        else:
            return self.grid.find_hex(self.x, self.y - 1)

    @property
    def hex_north_west(self):
        """ Returns the hex to the north west"""
        if self.x == 0:  # top of map
            return self.grid.find_hex(0, round(self.y / -1 + self.max_size))
        elif self.y == 0 and self.x % 2 == 0:  # left of map and even
            return self.grid.find_hex(self.x - 1, self.max_size)
        else:
            if self.x % 2 == 0:  # even
                return self.grid.find_hex(self.x - 1, self.y - 1)
            else:
                return self.grid.find_hex(self.x - 1, self.y)

    @property
    def hex_north_east(self):
        """ Returns the hex to the North East or None if end of map"""
        if self.x == 0:  # top of map
            return self.grid.find_hex(0, round(self.y / -1 + self.max_size))
        elif self.y == self.max_size and self.x % 2 == 1:  # right of map and x is odd
            return self.grid.find_hex(self.x - 1, 0)
        else:
            if self.x % 2 == 0:  # even
                return self.grid.find_hex(self.x - 1, self.y)
            else:
                return self.grid.find_hex(self.x - 1, self.y + 1)

    @property
    def hex_south_west(self):
        """ Returns the hex to the South West or None if end of map"""
        if self.x == self.max_size:  # bottom of map
            return self.grid.find_hex(self.max_size, round(self.y / -1 + self.max_size))
        elif self.y == 0 and self.x % 2 == 1:  # left of map and x is odd
            return self.grid.find_hex(self.x - 1, self.max_size)
        else:
            if self.x % 2 == 0:  # even
                return self.grid.find_hex(self.x + 1, self.y - 1)
            else:
                return self.grid.find_hex(self.x + 1, self.y)

    @property
    def hex_south_east(self):
        """ Returns the hex to the South East or None if end of map"""
        if self.x == self.max_size:  # bottom of map
            return self.grid.find_hex(self.max_size, round(self.y / -1 + self.max_size))
        elif self.y == self.max_size and self.x % 2 == 1:  # right of map and x is odd
            return self.grid.find_hex(self.x + 1, 0)
        else:
            if self.x % 2 == 0:  # even
                return self.grid.find_hex(self.x + 1, self.y)
            else:
                return self.grid.find_hex(self.x + 1, self.y + 1)

    @property
    def surrounding(self):
        """
         Returns a list of all surrounding hexes
         Returns: Hex
        """
        return [self.hex_east, self.hex_south_east, self.hex_south_west,
                self.hex_west, self.hex_north_west, self.hex_north_east]

    def bubble(self, distance=1):
        """
         Returns a list of all hexes within a certain number of hexes
        """
        around = self.surrounding
        if distance == 0:
            return self
        elif distance == 1:
            return around.append(self)
        try:
            return self.bubble_cache[distance]
        except KeyError:
            def step(iteration, hexes):
                if iteration < distance - 1:
                    temp = []
                    for h in hexes:
                        temp.extend(h.surrounding)
                    return step(iteration + 1, temp)
                else:
                    return hexes
            around.extend(step(0, around))
            final = list(set(around))
            self.bubble_cache[distance] = final
            return final


    @property
    def is_land(self):
        """
        Determines whether or not this is a land hex. (Altitude over sealevel)
        :return: Boolean
        """
        return self.altitude >= self.grid.sealevel

    @property
    def is_water(self):
        return self.is_land is False

    @property
    def type(self):
        if self.is_land:
            return HexType.land

        return HexType.ocean

    def is_inland(self):
        if self.is_land is False:
            return False
        around = [self.hex_west, self.hex_east,
                  self.hex_south_east, self.hex_south_west,
                  self.hex_north_east, self.hex_north_west]
        return all(x.is_land for x in around)

    @property
    def is_coast(self):
        return any(x.is_land for x in self.surrounding)

    def decide_slope(self, one, two):
        """ Returns UP, DOWN tuple """
        if one.altitude < two.altitude:
            return two, one
        return one, two

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __key(self):
        return self.x, self.y

    def __hash__(self):
        return hash(self.__key())

    @property
    def outer_edges(self):
        return [self.hex_north_east.edge_west, self.hex_north_west.edge_south_west,
                self.hex_west.edge_south_east, self.hex_south_west.edge_east,
                self.hex_south_east.edge_north_east, self.hex_east.edge_north_west]

    def calculate(self):
        """ Calculate the edges """
        h1 = self.hex_north_east
        h2 = self.hex_south_east
        up, down = self.decide_slope(h1, h2)
        self.edge_east = Edge(HexSide.east, self, self.hex_east, up, down)

        h1 = self.hex_north_west
        h2 = self.hex_south_west
        up, down = self.decide_slope(h1, h2)
        self.edge_west = Edge(HexSide.west, self, self.hex_west, up, down)

        h1 = self.hex_north_west
        h2 = self.hex_east
        up, down = self.decide_slope(h1, h2)
        self.edge_north_east = Edge(HexSide.north_east, self, self.hex_north_east, up, down)

        h1 = self.hex_south_west
        h2 = self.hex_east
        up, down = self.decide_slope(h1, h2)
        self.edge_south_east = Edge(HexSide.south_east, self, self.hex_south_east, up, down)

        h1 = self.hex_north_east
        h2 = self.hex_west
        up, down = self.decide_slope(h1, h2)
        self.edge_north_west = Edge(HexSide.north_west, self, self.hex_north_west, up, down)

        h1 = self.hex_south_east
        h2 = self.hex_west
        up, down = self.decide_slope(h1, h2)
        self.edge_south_west = Edge(HexSide.south_west, self, self.hex_south_west, up, down)

    def get_edge(self, side):
        if side is HexSide.east:
            return self.edge_east
        elif side is HexSide.south_east:
            return self.edge_south_east
        elif side is HexSide.south_west:
            return self.edge_south_west
        elif side is HexSide.west:
            return self.edge_west
        elif side is HexSide.north_west:
            return self.edge_north_west
        elif side is HexSide.north_east:
            return self.edge_north_east

    @property
    def edges(self):
        return [self.edge_east, self.edge_north_east, self.edge_north_west, self.edge_west,
                self.edge_south_west, self.edge_south_east]

    def __repr__(self):
        return "<HEX: X: {}, Y: {}, Z: {}>".format(self.x, self.y, self.altitude)


    @property
    def color_terrain(self):
        altitude = self.altitude
        hex_grid = self.grid

        if self.has_feature(HexFeature.lake):
            return 0, 0, 255

        map_type = self.grid.params.get('map_type')
        color_gradient = map_type.colors

        for level, color in color_gradient:
            if altitude < hex_grid.sealevel + level:
                return color
        return color_gradient[-1][1]

    @property
    def color_rivers(self):
        if self.is_water:
            if self.altitude < self.grid.sealevel - 10:
                color = (0, 20, 130)
            else:
                color = (0, 20, 170)
        else:
            if self.moisture < 5:
                color = (199,177,56)
            elif self.moisture < 10:
                color = (151,167,104)
            elif self.moisture < 15:
                color = (128,163,128)
            elif self.moisture < 20:
                color = (104,158,151)
            elif self.moisture < 25:
                color = (80,153,175)
            elif self.moisture < 30:
                color = (56,148,199)
            else:
                color = (56,148,199)

        if self.has_feature(HexFeature.lake):
            color = (0, 0, 255)

        return color

    @property
    def color_biome(self):
        if self.has_feature(HexFeature.glacier):
            return 204, 204, 204
        if self.is_land:
            return self.biome.color
        return 0, 20, 170

    @property
    def color_territories(self):
        if self.territory is None:
            return 200, 200, 200
        return self.territory.color

    @property
    def color_temperature(self):
        last_temp = -300
        for index, value in enumerate(TEMPERATURE_COLORS):
            temp, color = value
            if last_temp <= self.temperature <= temp:
                if self.is_land:
                    return color[0] - 20, color[1] - 20, color[2] - 20
                return color
            last_temp = temp
        return TEMPERATURE_COLORS[-1][1]

    @property
    def color_satellite(self):
        hex_grid = self.grid
        map_type = self.grid.params.get('map_type')
        if map_type is MapType.terran or map_type is MapType.oceanic:
            # if self.has_feature(HexFeature.lake):
            #     return 0, 20, 170
            # if self.is_land:
            #     colors = [h.biome.color for h in self.bubble(distance=2) if h.is_land]
            #     colors.append(self.biome.color)
            #     # colors is an array of 3-tuple colors

            #     mul = 1 / len(colors)
            #     avg_r = round(sum([mul * c[0] for c in colors]))
            #     avg_g = round(sum([mul * c[1] for c in colors]))
            #     avg_b = round(sum([mul * c[2] for c in colors]))
            #     return avg_r, avg_g, avg_b
            if self.has_feature(HexFeature.glacier):
                return randomize_color(Biome.arctic.color_satellite)

            if self.is_land:
                return randomize_color(lighten(self.biome.color_satellite, 0.9))
            # water
            for level, color in TERRAN_OCEAN_SATELLITE:
                if self.altitude < self.grid.sealevel + level:
                    return random.choice(color)
            return random.choice(TERRAN_OCEAN_SATELLITE[-1][1])
        elif map_type is MapType.glacial:
            for level, color in GLACIAL_SATELLITE:
                if self.altitude < self.grid.sealevel + level:
                    return randomize_color(color)
            return randomize_color(GLACIAL_SATELLITE[-1][1])
        elif map_type is MapType.volcanic:
            if self.biome is Biome.volcanic_liquid:
                return random.choice(VOLCANIC_LIQUID)
            else:
                def process(color):
                    r_color = randomize_color(color)
                    if self.biome is Biome.volcanic_molten_river:
                        b_color = Biome.volcanic_molten_river.color_satellite
                        return randomize_color(blend_colors(b_color, r_color))
                    return randomize_color(r_color)

                for level, color in VOLCANIC_SATELLITE:
                    if self.altitude < self.grid.sealevel + level:
                        return process(color)
                return process(VOLCANIC_SATELLITE[-1][1])
        else:
            if self.is_water:
                for level, color in TERRAN_OCEAN_SATELLITE:
                    if self.altitude < self.grid.sealevel + level:
                        return random.choice(color)
                return random.choice(TERRAN_OCEAN_SATELLITE[-1][1])

            # land
            if self.grid.params.get('pressure') < 0.003:
                color_list = BARREN_SATELLITE
            elif self.biome is Biome.barren_wet:
                color_list = BARREN_WET
            else:
                color_list = DUSTY_BARREN_SATELLITE

            def process(color):
                if self.biome is Biome.barren_ice_caps:
                    return randomize_color(blend_colors(color, Biome.barren_ice_caps.color))
                return randomize_color(color)

            for level, color in color_list:
                if self.altitude < self.grid.sealevel + level:
                    return process(color)

            return process(color)

    @property
    def color_pressure(self):
        """ Returns a season dict representing the map color of the pressure at summer and winter"""
        return (100, 100, 100)

from hexgen.edge import Edge
