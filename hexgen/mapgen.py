import uuid
import copy
import simplejson as json
import math
import random
import sys
sys.setrecursionlimit(10000)

from hexgen.constants import *
from hexgen.territory import Territory
from hexgen.enums import OceanType, HexResourceType, HexResourceRating, MapType, Hemisphere, GeoformType
from hexgen.geoform import Geoform
from hexgen.heightmap import Heightmap
from hexgen.grid import Grid
from hexgen.calendar import Calendar
from hexgen.util import decide_wind, pressure_at_seasons, Timer, is_isthmus, \
                        is_bay, is_strait, first_hex_without_geoform, is_peninsula

default_params = {
    "map_type": MapType.terran,
    "surface_pressure": 1013.25,
    "size": 100,
    "year_length": 365,
    "day_length": 24,
    "base_temp": 0,
    "avg_temp": 15,
    "sea_percent": 60,
    "hydrosphere": True,
    "ocean_type": OceanType.water,
    "random_seed": None,
    "roughness": 8,
    "height_range": (0, 255),
    "pressure": 1, # bar
    "axial_tilt": 23,

    # features
    "craters": False,
    "volanoes": False,

    "num_rivers": 50,

    # territories
    "num_territories": 0,

}


class MapGen:
    """ generates a heightmap as an array of integers between 1 and 255
    using the diamond-square algorithm"""

    def __init__(self, params, debug=False):
        """ initialize """
        self.params = default_params
        self.params.update(params)

        if debug:
            print("Making world with params:")
            for key, value in params.items():
                print("\t{}:\t{}".format(key, value))


        self.debug = debug

        if type(params.get('random_seed')) is int:
            random.seed(params.get('random_seed'))

        with Timer("Building Heightmap", self.debug):
            self.heightmap = Heightmap(self.params, self.debug)

        self.hex_grid = Grid(self.heightmap, self.params)
        if self.debug is True:
            print("\tAverage Height: {}".format(self.hex_grid.average_height))
            print("\tHighest Height: {}".format(self.hex_grid.highest_height))
            print("\tLowest Height: {}".format(self.hex_grid.lowest_height))

        print("Making calendar")
        self.calendar = Calendar(self.params.get('year_length'), self.params.get('day_length'))

        self.rivers = []
        self.rivers_sources = []

        with Timer("Computing hex distances", self.debug):
            self._get_distances()

        self._generate_pressure()


        if self.params.get('hydrosphere'):
            self._generate_rivers()

            # give coastal land hexes moisture based on how close to the coast they are
            # TODO: replace with more realistic model
            print("Making coastal moisture") if self.debug else False
            for y, row in enumerate(self.hex_grid.grid):
                for x, col in enumerate(row):
                    hex = self.hex_grid.grid[x][y]
                    if hex.is_land:
                        if hex.distance <= 5:
                            hex.moisture += 1
                        if hex.distance <= 3:
                            hex.moisture += random.randint(1, 3)
                        if hex.distance <= 1:
                            hex.moisture += random.randint(1, 6)

        # generate aquifers
        num_aquifers = random.randint(5, 25)

        if self.params.get('hydrosphere') is False or self.params.get('sea_percent') == 100:
            num_aquifers = 0

        print("Making {} aquifers".format(num_aquifers)) if self.debug else False
        aquifers = []
        while len(aquifers) < num_aquifers:
            rx = random.randint(0, len(self.hex_grid.grid) - 1)
            ry = random.randint(0, len(self.hex_grid.grid) - 1)
            hex = self.hex_grid.grid[rx][ry]
            if hex.is_land and hex.moisture < 5:
                aquifers.append(hex)

        for hex in aquifers:
            # print("Aquifer at ", hex)
            r1 = hex.bubble(distance=3)
            for hex in r1:
                if hex.is_land:
                    hex.moisture += random.randint(0, 2)
            r2 = hex.bubble(distance=2)
            for hex in r2:
                if hex.is_land:
                    hex.moisture += 1
            r3 = hex.surrounding
            for hex in r3:
                if hex.is_land:
                    hex.moisture += 1

        # decide terrain features
        print("Making terrain features") if self.debug else False
        # craters only form in barren planets with a normal or lower atmosphere
        if self.params.get('craters') is True:

            # decide number of craters
            num_craters = random.randint(0, 15)
            print("Making {} craters".format(num_craters))
            craters = []

            while len(craters) < num_craters:
                size = random.randint(1, 3)
                craters.append(dict(hex=random.choice(self.hex_grid.hexes),
                                    size=size,
                                    depth= 10 * size))

            for crater in craters:

                center_hex = crater.get('hex')
                size = crater.get('size')
                depth = crater.get('depth')
                hexes = []

                if size >= 1:
                    hexes = center_hex.surrounding
                    for h in hexes:
                        h.add_feature(HexFeature.crater)
                        h.altitude = center_hex.altitude - 5
                        h.altitude = max(h.altitude, 0)
                if size >= 2:
                    hexes = center_hex.bubble(distance=2)
                    for h in hexes:
                        h.add_feature(HexFeature.crater)
                        h.altitude = center_hex.altitude - 10
                        h.altitude = max(h.altitude, 0)

                if size >= 3:
                    hexes = center_hex.bubble(distance=3)
                    for h in hexes:
                        h.add_feature(HexFeature.crater)
                        h.altitude = center_hex.altitude - 15
                        h.altitude = max(h.altitude, 0)
                for h in hexes[:round(len(hexes)/3)]:
                    for i in h.surrounding:
                        if i.has_feature(HexFeature.crater) is False:
                            i.add_feature(HexFeature.crater)
                            i.altitude = center_hex.altitude - 20
                            i.altitude = max(i.altitude, 0)


        # volcanoes
        if self.params.get('volcanoes'):

            num_volcanoes = random.randint(0, 10)
            print("Making {} volcanoes".format(num_volcanoes))
            volcanoes = []
            while len(volcanoes) < num_volcanoes:
                center_hex = random.choice(self.hex_grid.hexes)
                if center_hex.altitude > 50:
                    size = random.randint(1, 5)
                    height = random.randint(30, 70)
                    volcanoes.append(dict(hex=center_hex, size=size, height=height))

            for volcano in volcanoes:
                height = volcano.get('height')
                size = volcano.get('size')
                center_hex = volcano.get('hex')
                print("\tVolcano: Size: {}, Height: {}".format(size, height))
                size_list = list(range(size))
                size_list.reverse()
                hexes = []
                for i in size_list:
                    i += 1
                    this_height = round(height / i)
                    if i == 1:
                        l = center_hex.surrounding + [center_hex]
                    else:
                        l = center_hex.bubble(distance=i)
                    for h in l:
                        hexes.append(h)
                        h.altitude = center_hex.altitude + this_height
                        h.add_feature(HexFeature.volcano)

                last_altitude = 0
                for h in hexes[:round(len(hexes)/2)]:
                    for i in h.surrounding:
                        if i.has_feature(HexFeature.volcano) is False:
                            i.add_feature(HexFeature.volcano)
                            i.altitude += 5
                            i.altitude = min(i.altitude, 255)
                            last_altitude = i.altitude
                center_hex.altitude += last_altitude + 5

                # lava flow
                def step(active_hex):
                    if active_hex.altitude < 50:
                        return
                    else:
                        active_hex.add_feature(HexFeature.lava_flow)
                        found = []
                        for i in active_hex.surrounding:
                            if i.altitude <= active_hex.altitude and i.has_feature(HexFeature.lava_flow) is False:
                                found.append(i)
                        found.sort(key=lambda x: x.altitude)
                        if len(found) > 1:
                            step(found[0])
                        if len(found) > 2:
                            step(found[1])

                step(center_hex)

        self.territories = []
        self.generate_territories()
        self.generate_resources()
        self.geoforms = []
        self._determine_landforms()

        print("Done") if self.debug else False

    def generate_resources(self):
        print("Placing resources")
        ratings = HexResourceRating.list()
        types = HexResourceType.list()

        combined = []

        for r in ratings:
            for t in types:
                combined.append(dict(rating=r,
                                     type=t))
        for h in self.hex_grid.hexes:
            for resource in combined:
                chance = (resource.get('rating').rarity *
                          resource.get('type').rarity * self.hex_grid.size / 1000 ) / (math.pow(self.hex_grid.size, 2))
                given = random.uniform(0, 1)
                if given <= chance:
                    h.resource = resource

    def generate_territories(self):
        """
         Makes territories
        """
        # select number of territories to place
        land_percent = 100 - self.params.get('sea_percent')
        num_territories = self.params.get('num_territories')

        # give each a land pixel to start
        print("Making {} territories".format(num_territories)) if self.debug else False

        c = 0
        if num_territories == 0:
            return
        while len(self.territories) < num_territories:
            rx = random.randint(0, len(self.hex_grid.grid) - 1)
            ry = random.randint(0, len(self.hex_grid.grid) - 1)
            hex_s = self.hex_grid.grid[rx][ry]
            if hex_s.is_land:
                color = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                self.territories.append(Territory(self.hex_grid, hex_s, c, color))
                c += 1

        # loop over each, adding hexes
        total_hexes = self.hex_grid.size * self.hex_grid.size
        count = 0
        while count < total_hexes:  #  i in range(0, 15):
            count = 0
            # print("Start: {} < {}".format(count, total_hexes))
            territories = self.territories
            random.shuffle(territories)
            for t in territories:
                frontier = t.frontier
                for f in frontier:
                    if f.is_owned is False:
                        f.territory = t
                        t.members.append(f)
                        t.last_added.append(f)
                count += t.size
            # print("End: {} < {}".format(count, total_hexes))

        # remove water hexes
        for t in self.territories:
            members = t.members
            t.members = [h for h in t.members if h.is_land]
            water_hexes = (h for h in members if h.is_water)
            for h in water_hexes:
                h.territory = None

        # merge territories
        print("Merging barren territories")

        if self.params.get('num_territories') > 0:
            top = []
            bottom = []
            for t in self.territories:
                avg_x = round(sum([i.x for i in t.members]) / len(t.members))
                if t.avg_temp < 0 and (avg_x / self.hex_grid.size) < 0.5:
                    top.append(t)
                elif t.avg_temp < 0 and (avg_x / self.hex_grid.size) >= 0.5:
                    bottom.append(t)

            pick_top = None
            pick_bottom = None
            if len(top) > 0:
                print("Merging {} territories from the top of the map".format( len(top) ))
                pick_top = random.choice(top)
                top.remove(pick_top)
                for t in self.territories:
                    if t in top:
                        pick_top.members += t.members
                        t.members = []

            if len(bottom) > 0:
                print("Merging {} territories from the bottom of the map".format( len(bottom) ))
                pick_bottom = random.choice(bottom)
                bottom.remove(pick_bottom)
                for t in self.territories:
                    if t in bottom:
                        pick_bottom.members += t.members
                        t.members = []

            if len(top) > 0:
                for h in pick_top.members:
                    h.territory = pick_top

            if len(bottom) > 0:
                for h in pick_bottom.members:
                    h.territory = pick_bottom

            self.territories = [t for t in self.territories if t is not None]

            print("{} empty territories being deleted".format(len([t for t in self.territories if len(t.members) == 0])))
            self.territories = [t for t in self.territories if len(t.members) > 0]

            print("There are now {} territories".format(len(self.territories)))

        print("Splitting territories into contiguous blocks") if self.debug else False
        for t in self.territories:
            t.find_groups()

    def _get_distances(self):
        """
        Gets the distances each land pixel is to the coastline.
        TODO: Make this more efficient
        """

        if not self.params.get('hydrosphere'):
            # we don't care about distances otherwise
            return

        for y, row in enumerate(self.hex_grid.grid):
            for x, col in enumerate(row):
                h = self.hex_grid.grid[x][y]
                if h.is_land:
                    count = 1
                    numbers = []

                    east = h.hex_east
                    while east.is_land is True and count < self.hex_grid.size * 2:
                        east = east.hex_east
                        count += 1
                    numbers.append(count)
                    count = 1

                    west = h.hex_west
                    while west.is_land is True and count < self.hex_grid.size * 2:
                        west = west.hex_west
                        count += 1
                    numbers.append(count)
                    count = 1


                    north_east = h.hex_north_east
                    while north_east.is_land is True and count < self.hex_grid.size * 2:
                        north_east = north_east.hex_north_east
                        count += 1
                    numbers.append(count)
                    count = 1


                    north_west = h.hex_north_west
                    while north_west.is_land is True and count < self.hex_grid.size * 2:
                        north_west = north_west.hex_north_west
                        count += 1

                    numbers.append(count)
                    count = 1


                    south_west = h.hex_south_west
                    while south_west.is_land is True and count < self.hex_grid.size * 2:
                        south_west = south_west.hex_south_west
                        count += 1
                    numbers.append(count)
                    count = 1

                    south_east = h.hex_south_east
                    while south_east.is_land is True and count < self.hex_grid.size * 2:
                        south_east = south_east.hex_south_east
                        count += 1
                    numbers.append(count)

                    h.distance = min(numbers)

    def _generate_pressure(self):

        with Timer("Generating pressure", self.debug):
            base_pressure = self.hex_grid.params.get('surface_pressure')

            with Timer("    calculating pressure zones", self.debug):
                # calcualte pressure caused by pressure zones
                pressure_diff = random.randint(3, 5)
                for y, row in enumerate(self.hex_grid.grid):
                    for x, col in enumerate(row):
                        h = self.hex_grid.grid[x][y]

                        # end_year is winter, mid_year is summer
                        if h.is_land:
                            max_shift = round(h.distance / 2)
                            end_year = pressure_at_seasons(h.latitude, base_pressure, pressure_diff, -max_shift)
                            mid_year = pressure_at_seasons(h.latitude, base_pressure, pressure_diff, max_shift)
                        else:
                            max_shift = min(6, 0.005 * round(self.hex_grid.sealevel - h.latitude))
                            end_year = pressure_at_seasons(h.latitude, base_pressure, pressure_diff, -max_shift)
                            mid_year = pressure_at_seasons(h.latitude, base_pressure, pressure_diff, max_shift)
                        h.pressure = (end_year, mid_year)

            # sort all hexes by land and water, lowest to highest
            with Timer("    sorting hexes into groups", self.debug):
                land_hexes = [h for h in self.hex_grid.hexes if h.is_land]
                water_hexes = [h for h in self.hex_grid.hexes if not h.is_land]
                land_hexes.sort(key=lambda x: x.altitude, reverse=True)
                water_hexes.sort(key=lambda x: x.altitude)

            def decide_change(h, incr):
                if h.is_land:
                    if h.hemisphere is Hemisphere.northern:
                        # winter / increase
                        # summer / decrease
                        return (h.pressure[0] + incr, h.pressure[1] - incr)
                    elif h.hemisphere is Hemisphere.southern:
                        # winter / decrease
                        # summer / increase
                        return (h.pressure[0] - incr, h.pressure[1] + incr)
                else:
                    if h.hemisphere is Hemisphere.northern:
                        # winter / decrease
                        # summer / increase
                        return (h.pressure[0] - incr, h.pressure[1] + incr)
                    elif h.hemisphere is Hemisphere.southern:
                        # winter / increase
                        # summer / decrease
                        return (h.pressure[0] + incr, h.pressure[1] - incr)
                    # return (h.pressure[0], h.pressure[1])

            def brush(percent, incr):
                matching_land_hexes = land_hexes[0:round(len(land_hexes) * percent)]
                matching_water_hexes = water_hexes[0:round(len(water_hexes) * percent)]

                for h in matching_land_hexes:
                    for h in h.bubble(3):
                        h.pressure = decide_change(h, incr * h.zone.incr)
                for h in matching_water_hexes:
                    for h in h.bubble(3):
                        h.pressure = decide_change(h, incr * h.zone.incr)

            brush(0.80, 0.05)
            brush(0.30, 0.10)
            brush(0.10, 0.10)

        # decide wind directions
        # Wind consists of a HexEdge direction and a magnitude that is equal to the difference in pressure
        # Wind direction is always to the neighbor with the lowest pressure,
        # deflected by the following rules:
        # Northern Hemisphere:
        #     high pressure areas: clockwise
        #     low pressure areas: counter-clockwise
        # Southern Hemisphere:
        #     high pressure areas: counter-clockwise
        #     low pressure areas: clockwise
        with Timer("Generating wind", self.debug):
            for y, row in enumerate(self.hex_grid.grid):
                for x, col in enumerate(row):
                    h = self.hex_grid.grid[x][y]
                    h.wind = (
                        decide_wind(0, base_pressure, h),
                        decide_wind(1, base_pressure, h)
                    )

        # IDEA 1
        # If hex is warmer than downstream: increase temperature downstream 20 hexes
        # If hex is colder than downstream: decrease temperature downstream 20 hexes
        # downstream hexes are neighboring hexes that have lower pressure
        # magnitude depends on pressure difference
        # Visit each hex. Steps: N*N*20 where N is map size

        # IDEA 2
        # going downstream, bring each hex's temperature close to the starting hex's temperature
        # less and less each loop, with loop 1 being very close and loop 20 being barely changed

        # IDEA 3
        # Visiting every hex, start a loop downstream until you reach a hex you have already visited
        # in this loop, averaging every hex's temperature with the last visited hex's temperature
        # weighted average favoring hex's base temperature when wind is less strong
        def windgust(season_index, starting_hex, loops=20):
            downstream_hex = starting_hex.wind[season_index].get('windward_hex')
            temp_change = ((20 / (loops + 1)) / 20) * 10
            if starting_hex.base_temperature[season_index] > downstream_hex.base_temperature[season_index]:
                # increase temperature at downstream hex
                downstream_hex.wind_temp_effect[season_index] = temp_change / 2
                # decrease temperature at this hex
                starting_hex.wind_temp_effect[season_index] = -(temp_change / 2)
            else:
                # decrease temperature at downstream hex
                downstream_hex.wind_temp_effect[season_index] = -(temp_change / 2)
                # increase temperature at this hex
                starting_hex.wind_temp_effect[season_index] = temp_change / 2

            # go on to the next hex in line
            if loops != 0:
                next_hex = downstream_hex.wind[season_index].get('windward_hex')
                windgust(season_index, next_hex, loops - 1)


        with Timer("Generating Temperature Changes", self.debug):
            for y, row in enumerate(self.hex_grid.grid):
                for x, col in enumerate(row):
                    h = self.hex_grid.grid[x][y]

                    # end year
                    windgust(0, h)

                    # mid year
                    windgust(1, h)


    def _generate_rivers(self):
        """
        For each river source edge:
            If the "down" hex of the left edge is the "one" or "two" hexes of this edge,
                the left edge is invalid
            If the "down" hex of the right edge is the "one" or "two" hexes of this edge,
                the right edge is invalid
            If two are valid:
                E = lowest slope edge
                If E.down is below sea level, end here
                otherwise add this edge as a river segment
            else if one is valid:
                E = valid edge
                If E.down is below sea level, end here
                otherwise add this edge as a river segment
            else if both are invalid:
                Make a lake at the lowest of the "one" or "two" hexes of this edge
                Make a new river source edge at an random edge pointing out from this lake
                    that has a direction pointing out from the lake
        """
        land_percent = 100 - self.params.get('sea_percent')
        num_rivers = self.params.get('num_rivers')
        print("Making {} rivers".format(num_rivers)) if self.debug else False

        while len(self.rivers_sources) < num_rivers:
            rx = random.randint(0, self.hex_grid.size - 1)
            ry = random.randint(0, self.hex_grid.size - 1)
            hex_s = self.hex_grid.find_hex(rx, ry)
            if hex_s.is_inland and hex_s.altitude > self.hex_grid.sealevel + 35:
                # if hex_s.temperature < 0:
                # TODO: Determine when to not place rivers at hight latitudes
                #     # don't place rivers above +35 altitude when the temperature is below zero
                #     continue
                random_side = random.choice(list(HexSide))
                #print("Placing river source at {}, {}".format(rx, ry))
                self.rivers_sources.append(RiverSegment(self.hex_grid, rx, ry, random_side, True))

        print("Placed river sources") if self.debug else False

        for r in self.rivers_sources: # loop over each source segment
            segment = r # river segment we are looking at
            finished = False
            last_unselected = None
            # we stop only when one of two things happen:
            #   - a lake is formed
            #   - we reached sea level
            while finished is False:
                # print("Segment: {}, {}".format(segment.x, segment.y))
                side_one, side_two = segment.side.branching(segment.edge.direction)
                down = segment.edge.down  # down-slope hex of this segment

                # add the moisture to the one and two hexes in a 3 radius
                one = segment.edge.one.bubble(distance=3)
                two = segment.edge.two.bubble(distance=3)
                both = list(set(one + two))
                for hex in both:
                    if hex.is_land:
                        hex.moisture += 1
                three = segment.edge.one.surrounding
                four = segment.edge.two.surrounding
                both = list(set(three + four))
                for hex in both:
                    if hex.is_land:
                        hex.moisture += 1

                # find the two Edges from the sides found branching
                edge_one = down.get_edge(side_one)
                edge_two = down.get_edge(side_two)

                # check if either of the edges are valid river segment locations
                one_valid = True
                two_valid = True
                if edge_one.down == segment.edge.one or edge_one.down == segment.edge.two:
                    one_valid = False
                if edge_two.down == segment.edge.one or edge_two.down == segment.edge.two:
                    two_valid = False

                if self.is_river(edge_one):
                    one_valid = False
                elif self.is_river(edge_two):
                    two_valid = False

                if one_valid and two_valid:
                    # print("\tBoth are valid edges")
                    if edge_one.down.altitude < edge_two.down.altitude:
                        selected = edge_one
                        selected_side = side_one
                        last_unselected = edge_two, side_two
                    else:
                        selected = edge_two
                        selected_side = side_two
                        last_unselected = edge_one, side_one
                    if selected.down.altitude < self.hex_grid.sealevel:
                        finished = True
                    segment.next = RiverSegment(self.hex_grid, selected.one.x, selected.one.y, selected_side, False)
                    segment = segment.next
                elif one_valid is True and two_valid is False:
                    # print("\tOne is Valid")
                    selected = edge_one
                    last_unselected = edge_two, side_two
                    if selected.down.altitude < self.hex_grid.sealevel:
                        finished = True
                    segment.next = RiverSegment(self.hex_grid, selected.one.x, selected.one.y, side_one, False)
                    segment = segment.next
                elif one_valid is False and two_valid is True:
                    # print("\tTwo is valid")
                    selected = edge_two
                    last_unselected = edge_one, side_one
                    if selected.down.altitude < self.hex_grid.sealevel:
                        finished = True
                    segment.next = RiverSegment(self.hex_grid, selected.one.x, selected.one.y, side_two, False)
                    segment = segment.next
                else:
                    # import ipdb; ipdb.set_trace()
                    # segment.x = last_unselected[0].one.x
                    # segment.y = last_unselected[0].one.y
                    # segment.side = last_unselected[1]
                    # segment.is_source = True
                    # finished = True
                    # print("huh?")

                    # both edges are invalid, make lake at one or two
                    # if segment.edge.one.altitude < segment.edge.two.altitude:
                    #     lake = segment.edge.one
                    # else:
                    #     lake = segment.edge.two
                    # lake.add_feature(HexFeature.lake)

                    # moisture around lake increases
                    # surrounding = lake.surrounding
                    # for hex in surrounding:
                    #     if hex.is_land:
                    #         hex.moisture += 3

                    # print("\tMade a lake at {}, {}".format(segment.x, segment.y))

                    # make a new source river at an outer edge of the lake
                    # chosen_edge = random.choice(lake.outer_edges)
                    # self.rivers_sources.append(RiverSegment(self.hex_grid, chosen_edge.one.x, chosen_edge.one.y, chosen_edge.side, True))

                    finished = True

        final = []

        for r in self.rivers_sources:
            # remove rivers that are too small
            if r.size > 2:
                final.append(r)
                while r.next is not None:
                    # print("Segment: ", r.next)
                    final.append(r.next)
                    r = r.next
        for r in final:
            r.edge.is_river = True
        self.rivers = final

    def _determine_landforms(self):
        # single hex geoforms
        with Timer("Finding geographic features", self.debug):
            with Timer("\tPlacing initial geoforms", self.debug):
                for y, row in enumerate(self.hex_grid.grid):
                    for x, col in enumerate(row):
                        h = self.hex_grid.grid[x][y]

                        # Isthmus
                        if is_isthmus(h):
                            h.geoform_type = GeoformType.isthmus

                        # Bays
                        if is_bay(h):
                            h.geoform_type = GeoformType.bay

                        # Straits
                        if is_strait(h):
                            h.geoform_type = GeoformType.strait

                        # Peninsula
                        if is_peninsula(h):
                            h.geoform_type = GeoformType.peninsula

                        if h.geoform_type is not None:
                            self.geoforms.append(Geoform(set([h]), h.geoform_type))

            def flood(found, current, hex_type):
                """ Do a flood fill at this hex over all hexes of this type without geoforms """
                if current.geoform_type is not None:
                    return set()
                if current in found:
                    return set()
                neighbors = [h[1] for h in current.neighbors]
                found.add(current)
                for neighbor in neighbors:
                    if neighbor.type is hex_type:
                        found.update(flood(found, neighbor, hex_type))
                return found

            def give_geoform(hexes, geoform_type):
                for h in hexes:
                    h.geoform_type = geoform_type

            # loop until every fucking hex has a geoform
            # import ipdb; ipdb.set_trace()
            with Timer("\tFinding contiguous geoforms", self.debug):
                sys.setrecursionlimit(10000)
                current = first_hex_without_geoform(self.hex_grid.grid)
                while current is not None:
                    if current.is_land:
                        # try to find continents
                        hexes = flood(set(), current, current.type)
                        if len(hexes) < 25:
                            geotype = GeoformType.small_island
                        elif len(hexes) < 100:
                            geotype = GeoformType.large_island
                        else:
                            geotype = GeoformType.continent
                    else:
                        # try to find oceans
                        hexes = flood(set(), current, current.type)
                        if len(hexes) < 3:
                            geotype = GeoformType.lake
                        elif len(hexes) < 100:
                            geotype = GeoformType.sea
                        else:
                            geotype = GeoformType.ocean

                    give_geoform(hexes, geotype)
                    # hexes is a set of hexes
                    self.geoforms.append(Geoform(hexes, geotype))
                    # find a new hex
                    current = first_hex_without_geoform(self.hex_grid.grid)

            # now we have geoforms

            # FIND NEIGHBORING GEOFORMS
            def calculate_neighbors():
                """ recalculate neighboring geoforms """
                for geoform in self.geoforms:
                    geoform.neighbors.clear()
                    for h in geoform.hexes:
                        ng = [n[1].geoform for n in h.neighbors if n[1].geoform is not geoform]
                        geoform.neighbors.update(ng)
                    assert geoform not in geoform.neighbors, 'A Geoform should not be in its own neighbors set'
            calculate_neighbors()

            with Timer("\tMerging geoforms", self.debug):
                # MERGE GEOFORMS
                # merge all neighboring geoforms of like type
                for geoform in self.geoforms:
                    for neighbor in geoform.neighbors:
                        if geoform.type is neighbor.type:
                            # remove neighbor
                            print('Merging {} '.format(geoform.type))
                            geoform.merge(neighbor)

                calculate_neighbors()

                # if an island is next to a continent or island separated by an isthmus,
                # and that island doesn't have any other isthmuses
                # the island becomes a peninsula
                for geoform in self.geoforms:
                    if geoform.type is GeoformType.isthmus:
                        islands = geoform.neighbor_of_type(GeoformType.small_island)
                        land_form = geoform.neighbor_of_types([GeoformType.continent,
                                                               GeoformType.small_island,
                                                               GeoformType.large_island])

                        if len(islands) == 1 and len(land_form) == 1 and \
                            len(land_form[0].neighbors) >= 2:
                            other_isthmuses = len(islands[0].neighbor_of_type(GeoformType.isthmus)) > 1
                            # check to see if this island has other isthmuses
                            # if it does, exclude it
                            if other_isthmuses is False:
                                print('Merging island + isthmus into peninsula')
                                islands[0].merge(geoform) # merge the island and the isthmus
                                islands[0].type = GeoformType.peninsula # change island to peninsula

                calculate_neighbors()

                # small islands separated by an isthmus to a large island should
                # be merged into the large island
                for geoform in self.geoforms:
                    if geoform.type is GeoformType.small_island:
                        large_islands = geoform.neighbor_of_type(GeoformType.large_island)
                        if len(large_islands) > 0:
                            print('Merging small island into large island')
                            large_islands[0].merge(geoform)

                calculate_neighbors()



                # islands separated by an isthmus with a continent should be merged
                # TODO: maybe large islands should be a new continent
                for geoform in self.geoforms:
                    if geoform.type is GeoformType.large_island or \
                       geoform.type is GeoformType.small_island:
                        isthmuses = geoform.neighbor_of_type(GeoformType.isthmus)
                        continents = set()
                        for i in isthmuses:
                            continents.update(i.neighbor_of_type(GeoformType.continent))
                        continents = list(continents)
                        if len(continents) == 1:
                            # one continent neighbor
                            print('Merging island into continent')
                            continents[0].merge(geoform)
                        elif len(continents) > 1:
                            # multiple continents are neighbors
                            print('Merging island and other continents into one continent')
                            continents[0].merge(geoform)
                            for c in continents[1:]:
                                continents[0].merge(c)

                calculate_neighbors()

                # if a peninsula is next to a isthmus, merge them into one peninsula
                for geoform in self.geoforms:
                    if geoform.type is GeoformType.peninsula:
                        isthmuses = geoform.neighbor_of_type(GeoformType.isthmus)
                        if len(isthmuses) == 1:
                            print('Merging isthmus into peninsula')
                            geoform.merge(isthmuses[0])

                        # a peninsula of size 2 with no neighbors is an island
                        if geoform.size == 2 and len(geoform.neighbors) == 0:
                            geoform.type = GeoformType.small_island

                calculate_neighbors()

                # remove old geoforms
            print("Deleting {} geoforms".format(len([g for g in self.geoforms if g.to_delete is True])))
            self.geoforms = [g for g in self.geoforms if g.to_delete is False]
            print("There is now {} geoforms".format(len(self.geoforms)))

    def is_river(self, edge):
        """
        Determines if an edge has a river
        :param edge: Edge
        :return: Boolean
        """
        for r in self.rivers_sources:
            while r.next is not None:
                if r.edge == edge:
                    return True
                r = r.next
        return False

    def find_river(self, x, y):
        """ Finds river segments at an hex's x and y coordinates. Returns a list of EdgeSides
            representing where the river segments are """
        seg = []
        for s in self.rivers:
            if s.x == x and s.y == y:
                seg.append(s.side)
        return seg

    def export(self, filename):
        """ Export the map data as a JSON file """
        with Timer("Compiling data into dictionary", self.debug):
            params = copy.copy(self.params)
            params['map_type'] = params.get('map_type').to_dict()
            params['ocean_type'] = params.get('ocean_type').to_dict()
            data = {
                "parameters": params,
                "details": {
                    "size": self.hex_grid.size,
                    "sea_level": self.hex_grid.sealevel,
                    "avg_height": self.hex_grid.average_height,
                    "max_height": self.hex_grid.highest_height,
                    "min_height": self.hex_grid.lowest_height
                },
                "hexes": [],
                "geoforms": []
            }
            def edge_dict(edge):
                return dict(
                    is_river=edge.is_river,
                    is_coast=edge.is_coast,
                    direction=edge.direction.name
                )
            for x, row in enumerate(self.hex_grid.grid):
                row_data = []
                for y, col in enumerate(row):
                    h = self.hex_grid.find_hex(x, y)
                    color_temperature = (
                        (h.color_temperature[0][0] + h.color_temperature[1][0]) / 2,
                        (h.color_temperature[0][1] + h.color_temperature[1][1]) / 2,
                        (h.color_temperature[0][2] + h.color_temperature[1][2]) / 2
                    )
                    temperature = round((h.temperature[0] + h.temperature[1]) / 2, 2)
                    row_data.append({
                        "id": h.id.hex,
                        "x": x,
                        "y": y,
                        "altitude": h.altitude,
                        "temperature": temperature,
                        "moisture": h.moisture,
                        "biome": h.biome.to_dict(),
                        "type": h.type.name,
                        "is_inland": h.is_inland,
                        "is_coast": h.is_coast,
                        "geoform": h.geoform.id.hex,
                        "colors": {
                            "satellite": h.color_satellite,
                            "terrain": h.color_terrain,
                            "temperature": color_temperature,
                            "biome": h.color_biome,
                            "rivers": h.color_rivers
                        },
                        "edges": {
                            "east": edge_dict(h.edge_east),
                            "north_east": edge_dict(h.edge_north_east),
                            "north_west": edge_dict(h.edge_north_west),
                            "west": edge_dict(h.edge_west),
                            "south_west": edge_dict(h.edge_south_west),
                            "south_east": edge_dict(h.edge_south_east)
                        }
                    })
                data['hexes'].append(row_data)
            for geoform in self.geoforms:
                data['geoforms'].append(geoform.to_dict())
        with open(filename, 'w') as outfile:
            with Timer("Writing data to JSON file", self.debug):
                json.dump(data, outfile)
        return data

from hexgen.river import RiverSegment
from hexgen.hex import Hex, HexSide, HexFeature
