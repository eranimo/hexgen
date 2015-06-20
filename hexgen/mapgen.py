import math
import random
import sys
sys.setrecursionlimit(1500)

from hexgen.constants import *
from hexgen.territory import Territory
from hexgen.enums import OceanType, HexResourceType, HexResourceRating, MapType
from hexgen.heightmap import Heightmap
from hexgen.grid import Grid

default_params = {
    "map_type": MapType.terran,
    "surface_pressure": 100,
    "size": 100,
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

        self.heightmap = Heightmap(self.params)

        self.hex_grid = Grid(self.heightmap, self.params)

        self.rivers = []
        self.rivers_sources = []

        print("Computing hex distances") if self.debug else False
        self._get_distances()


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
                if hex_s.temperature < 0:
                    # don't place rivers above +35 altitude when the temperature is below zero
                    continue
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
                    if segment.edge.one.altitude < segment.edge.two.altitude:
                        lake = segment.edge.one
                    else:
                        lake = segment.edge.two
                    lake.add_feature(HexFeature.lake)

                    # moisture around lake increases
                    surrounding = lake.surrounding
                    for hex in surrounding:
                        if hex.is_land:
                            hex.moisture += 3

                    # print("\tMade a lake at {}, {}".format(segment.x, segment.y))
                    #
                    # # make a new source river at an outer edge of the lake
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
        self.rivers = final

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


from hexgen.river import RiverSegment
from hexgen.hex import Hex, HexSide, HexFeature
