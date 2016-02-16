import math
import random
import time

from hexgen.enums import HexEdge, Hemisphere

import collections
import functools
from itertools import combinations

class memoized(object):
    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    '''
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
        return value
    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__
    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)

def blend_colors(color1, color2):
    return min(round((color1[0] + color2[0]) / 2), 255), \
           min(round((color1[1] + color2[1]) / 2), 255), \
           min(round((color1[2] + color2[2]) / 2), 255)

def lighten(color, amount):
    return min(round(color[0] + color[0] * amount), 255), \
           min(round(color[1] + color[1] * amount), 255), \
           min(round(color[2] + color[2] * amount), 255)

def randomize_color(color, dist=1):
    colors = [
        color,
        (color[0] - dist, color[dist] - dist, color[2] - dist),
        (color[0] + dist, color[dist] + dist, color[2] + dist),
        (color[0] - dist, color[dist] + dist, color[2] - dist),
        (color[0] + dist, color[dist] - dist, color[2] - dist),
        (color[0] - dist, color[dist] + dist, color[2] - dist),
        (color[0] - dist, color[dist] - dist, color[2] + dist),
        (color[0] + dist, color[dist] - dist, color[2] + dist),
        (color[0] - dist, color[dist] + dist, color[2] - dist)
    ]
    return random.choice(colors)

def latitude_to_number(latitude, map_size):
    """ Converts latitude in degrees (north is positive, south is negative) to a number
    corresponding to the latitude grid position """
    return (map_size / 2) - ((latitude / 90) * (map_size / 2))


def pressure_at_seasons(latitude, base_pressure, pressure_diff, itcz_rise):
    """
    latitude = latitude in degrees
    base_pressure = the base surface atmospheric pressure at this planet in millibars
    pressure_diff = the max difference in pressure at each zone
    itcz_rise = the rise in altitude of the ITCZ at this season at this latitude
    """
    itcz = (-10 + itcz_rise, 10 + itcz_rise)
    sthz = dict(north=(20 + itcz_rise, 40 + itcz_rise),
                south=(-40 + itcz_rise, -20 + itcz_rise))
    pf = dict(north=(50 + itcz_rise, 70 + itcz_rise),
              south=(-70 + itcz_rise, -50 + itcz_rise))

    if itcz[0] <= latitude <= itcz[1]: # ITCZ
        # highest around 0 degrees
        final_pressure = base_pressure - (-math.pow(latitude - itcz_rise, 2) + 100) * (pressure_diff / 100)
    elif sthz.get('south')[0] <= latitude <= sthz.get('south')[1]: # southern STHZ
        # highest around -30 degrees
        final_pressure = base_pressure + ((-math.pow(latitude + (30 - itcz_rise), 2) + 100) / 100) * pressure_diff
    elif sthz.get('north')[0] <= latitude <= sthz.get('north')[1]: # northern STHZ
        # highest around 30 degrees
        final_pressure = base_pressure + ((-math.pow(latitude - (30 + itcz_rise), 2) + 100) / 100) * pressure_diff
    elif pf.get('south')[0] <= latitude <= pf.get('south')[1]: # southern PF
        # highest around -60 degrees
        final_pressure = base_pressure - ((-math.pow(latitude + (60 - itcz_rise), 2) + 100) / 100) * (pressure_diff / 2)
    elif pf.get('north')[0] <= latitude <= pf.get('north')[1]: # northern PF
        # highest around 60 degrees
        final_pressure = base_pressure - ((-math.pow(latitude - (60 + itcz_rise), 2) + 100) / 100) * (pressure_diff / 2)
    else:
        final_pressure = base_pressure + random.randint(-1, 1)
    return round(final_pressure)

@memoized
def clockwise_hex_edge(hex_edge, reverse=False):
    """
    Given a HexEdge, return the clockwise hex edge.
    If reverse if True, return the anti-clockwise hex edge
    """
    if hex_edge is HexEdge.east:
        return HexEdge.south_east if not reverse else HexEdge.north_east
    elif hex_edge is HexEdge.south_east:
        return HexEdge.south_west if not reverse else HexEdge.east
    elif hex_edge is HexEdge.south_west:
        return HexEdge.west if not reverse else HexEdge.south_east
    elif hex_edge is HexEdge.west:
        return HexEdge.north_west if not reverse else HexEdge.south_west
    elif hex_edge is HexEdge.north_west:
        return HexEdge.north_east if not reverse else HexEdge.west
    elif hex_edge is HexEdge.north_east:
        return HexEdge.east if not reverse else HexEdge.north_west


def decide_wind(season_index, world_pressure, hexagon):
    """
    Decide the direction and magnitude of wind at a hex
    season_index = 0 for end_year, 1 for mid_year
    world_pressure = the world's average surface air pressure
    hexagon = which hexagon we're making wind for
    """
    lowest_neighbor = min(hexagon.neighbors, key=lambda h: h[1].pressure[season_index])
    wind_direction = lowest_neighbor[0]

    neighbor = hexagon.neighbor_at(wind_direction)
    if neighbor.pressure[season_index] == hexagon.pressure[season_index]:
        return {
            "direction": None,
            "windward_hex": neighbor,
            "pressure_diff": 0
        }

    if hexagon.hemisphere is Hemisphere.northern:
        if hexagon.pressure[season_index] <= world_pressure: # low pressure
            corrected_wind_direction = clockwise_hex_edge(wind_direction, True)
        else: # high pressure
            corrected_wind_direction = clockwise_hex_edge(wind_direction)
    else:
        if hexagon.pressure[season_index] <= world_pressure: # low pressure
            corrected_wind_direction = clockwise_hex_edge(wind_direction)
        else: # high pressure
            corrected_wind_direction = clockwise_hex_edge(wind_direction, True)

    windward_hex = hexagon.neighbor_at(wind_direction)
    pressure_diff = abs(hexagon.pressure[season_index] - windward_hex.pressure[season_index])

    return {
        "direction": corrected_wind_direction,
        "windward_hex": windward_hex,
        "pressure_diff": pressure_diff
    }


class Timer:
    def __init__(self, text, debug=True):
        self.text = text
        self.debug = debug

    def __enter__(self):
        if self.debug:
            print(self.text.ljust(50), end="")
            print('starting...')
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start
        if self.debug:
            print(self.text.ljust(50), end="")
            print("finished after {:0.03f} ms\n".format(self.interval * 1000))

@memoized
def is_opposite_hex(my_side, other_side, strict=False):
    """
        Given two HexEdges, are they opposite of each other?

        A hex is opposite of another in the following circumstances:

        W -> NE, E, SE
        NW -> E, SE, SW
        NE -> SE, SW, W
        E -> NW, W, SW
        SE -> NE, NW, W
        SW -> E, NE, NW
    """
    opp = {}
    opp[HexEdge.west]       = [HexEdge.east, HexEdge.north_east, HexEdge.south_east]
    opp[HexEdge.north_west] = [HexEdge.south_east, HexEdge.east, HexEdge.south_west]
    opp[HexEdge.north_east] = [HexEdge.south_west, HexEdge.south_east, HexEdge.west]
    opp[HexEdge.east]       = [HexEdge.west, HexEdge.north_west, HexEdge.south_west]
    opp[HexEdge.south_east] = [HexEdge.north_west, HexEdge.north_east, HexEdge.west]
    opp[HexEdge.south_west] = [HexEdge.north_east, HexEdge.east, HexEdge.north_west]

    if strict:
        return other_side is opp[my_side][0]
    return other_side in opp[my_side]

def is_isthmus(h):
    if h.is_water:
        return False
    water_neighbors = [h for h in h.neighbors if h[1].is_water]
    if len(water_neighbors) == 2:
        # if we have two water hexes in our neighbors,
        # and any one of them are opposite of another one,
        # we have an isthmus
        for one, two in combinations(water_neighbors, 2):
            if is_opposite_hex(one[0], two[0]):
                return True
    return False

def is_peninsula(h):
    """ A hex is a peninsula if it has only one land neighbor """
    if h.is_water:
        return False
    land_neighbors = [h for h in h.neighbors if h[1].is_land]
    return len(land_neighbors) == 1

def is_bay(h):
    if h.is_land:
        return False
    water_neighbors = [h for h in h.neighbors if h[1].is_water]
    return len(water_neighbors) == 1

def is_strait(h):
    if h.is_land:
        return False
    water_neighbors = [h for h in h.neighbors if h[1].is_water]
    if len(water_neighbors) == 2:
        return is_opposite_hex(water_neighbors[0][0], water_neighbors[1][0])
    return False

def first_hex_without_geoform(hexes):
    for y, row in enumerate(hexes):
        for x, col in enumerate(row):
            h = hexes[x][y]
            if h.geoform_type is None:
                return h
    return None
