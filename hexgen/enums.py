from enum import Enum

from hexgen.constants import TERRAIN_BARREN, TERRAIN_TERRAN, TERRAIN_OCEANIC


class SuperEnum(Enum):
    """ Adds an id property that gets the order of an enum member in the class  """

    def __init__(self, *args):
        for key, value in enumerate(args):
            for namekey, name in enumerate(self.__keys__):
                if key == namekey:
                    setattr(self, name, value)

    def to_dict(self):
        """ converts an enum member to a dict """
        rep = dict([(key, getattr(self, key)) for key in self.__keys__])
        rep['name'] = self.name
        return rep

    @classmethod
    def get(cls, id_):
        l = [item for item in list(cls.__members__) if getattr(cls[item], 'id') == id_]
        if l is not None and len(l) > 0:
            return cls[l[0]]
        else:
            return None

    @classmethod
    def items(cls):
        return list(cls.__members__)

    @classmethod
    def pluck(cls, key='name'):
        return [getattr(cls[x], key) for x in list(cls.__members__)]

    @classmethod
    def dump(cls):
        return [cls[x].to_dict() for x in list(cls.__members__)]

    @classmethod
    def all(cls):
        return [cls[x].to_dict() for x in list(cls.__members__)]

    @classmethod
    def members(cls):
        return [cls[x].name for x in list(cls.__members__)]

    @classmethod
    def list(cls):
        return [cls[x] for x in list(cls.__members__)]


class Biome(SuperEnum):
    __keys__ = ['id', 'code', 'title', 'color', 'base_fertility', 'color_satellite']

    lifeless =             (13, 'l', 'Lifeless',              (200, 200, 200), 0,  (150, 150, 150))

    # terran
    arctic =               (1, 'a', 'Arctic',                 (224, 224, 224), 1,  (132, 152, 159))
    tundra =               (2, 'u', 'Tundra',                 (114, 153, 128), 15, (52, 55, 44))
    alpine_tundra =        (3, 'p', 'Alpine Tundra',          (97, 130, 106),  10, (103, 91, 61))
    desert =               (4, 'd', 'Desert',                 (237, 217, 135), 5,  (94, 78, 52))
    shrubland =            (5, 's', 'Shrubland',              (194, 210, 136), 20, (58, 47, 21))
    savanna =              (6, 'S', 'Savanna',                (219, 230, 158), 80, (66, 53, 28))
    grasslands =           (7, 'g', 'Grasslands',             (166, 223, 106), 150, (45, 46, 22))
    boreal_forest =        (8, 'b', 'Boreal Forest',          (28, 94, 74),    30, (36, 41, 29))
    temperate_forest =     (9, 't', 'Temperate Forest',       (76, 192, 0),    100, (40, 37, 19))
    temperate_rainforest = (10, 'T', 'Temperate Rainforest',  (89, 129, 89),   100, (42, 38, 21))
    tropical_forest =      (11, 'r', 'Tropical Forest',       (96, 122, 34),   70, (32, 39, 21))
    tropical_rainforest =  (12, 'R', 'Tropical Rainforest',   (0, 70, 0),      60, (26, 33, 16))

    # BARREN
    # color: grey if no atmosphere ( less than 0.003 earth pressure),
    #   red if atmosphere (greater than 0.003 earth pressure),
    #   tan if atmosphere and water
    # - highlands   light
    # - lowlands    dark
    barren_dusty = (14, 'bld', 'Barren Drylands', (87, 26, 27), 0)

    barren = (16, 'bld', 'Barren Drylands', (43, 44, 35), 0)
    barren_wet = (21, 'bw', "Barren Wetland", (77, 36, 37), 0, (22, 51, 61))

    barren_ice_caps = (18, 'bi', 'Barren Ice Caps', (242, 228, 216), 0)

    # VOLCANIC
    # color: greyish light brown with red lava flows
    # - lava plains     red
    # - highlands       ligh
    # - lowlands        dark
    volcanic_liquid = (19, 'mo', "Lava Fields", (217, 0, 0), 0)
    volcanic_molten_river = (19, 'mo', "Lavaflow", (207, 10, 10), 0, (207, 10, 10))
    volcanic_solid = (20, 'so', "Basaltic Plains", (40, 28, 25), 0)


class OceanType(SuperEnum):
    __keys__ = ['id', 'title']

    water = (1, "Water")
    magma = (2, "Magma")
    hydrocarbons = (3, "Hydrocarbons")

class HexResourceRating(SuperEnum):
    """ ((1 + 1) * 60/1000 ) / (60 ^ 2) * 10000
    """
    __keys__ = ['id', 'title', 'rarity', 'multiplier']

    poor =     (1, "Poor",    10, 4)
    average =  (2, "Average", 6,  3)
    rich =     (3, "Rich",    3,  2)
    abundant = (4, "Abundant", 1, 1)


class HexResourceType(SuperEnum):
    __keys__ = ['id', 'rarity', 'title', 'material', 'yield', 'color']

    iron_vein =      (1, 15, "Iron Vein",      1000, 'commonmetals', (100, 0, 0))
    copper_vein =    (2, 15, "Copper Vein",    1000, 'commonmetals', (0, 100, 0))
    silver_vein =    (3, 15, "Silver Vein",    1000, 'commonmetals', (0, 0, 100))
    lead_vein =      (4, 15, "Lead Vein",      1000, 'commonmetals', (100, 0, 100))
    aluminum_vein =  (5, 15, "Aluminum Vein",  1000, 'commonmetals', (50, 150, 50))
    tin_vein =       (6, 15, "Tin Vein",       1000, 'commonmetals', (150, 50, 50))
    titanium_vein =  (7, 15, "Titanium Vein",  1000, 'commonmetals', (200, 50, 200))
    magnesium_vein = (8, 15, "Magnesium Vein", 1000, 'commonmetals', (50, 200, 50))

    gold_ore_deposit =       (9,  1, "Gold Ore Deposit",       500, 'preciousmetals', (255, 0, 0))
    chromite_ore_deposit =   (10, 3, "Chromite Ore Deposit",   500, 'preciousmetals', (255, 255, 0))
    monazite_ore_deposit =   (11, 5, "Monazite Ore Deposit",   500, 'preciousmetals', (0, 0, 255))
    bastnasite_ore_deposit = (12, 4, "Bastnasite Ore Deposit", 500, 'preciousmetals', (0, 125, 200))
    xenotime_ore_deposit =   (13, 1, "Xenotime Ore Deposit",   500, 'preciousmetals', (200, 125, 0))

    graphite_deposit =    (14, 10, "Graphite Deposit",   1500, 'carbon', (0, 0, 0))
    coal_deposit =        (15, 30, "Coal Deposit",       1500, 'carbon', (255, 255, 255))

    quartz_deposit =      (16, 7, "Quartz Vein",         1000, 'silicon', (80, 80, 80))

    uranium_ore_deposit = (17, 1, "Uranium Ore Deposit", 10, 'uranium', (255, 50, 50))


class HexEdge(SuperEnum):
    __keys__ = ['id', 'title']
    east       = (1, 'East')
    north_east = (2, 'North East')
    north_west = (3, 'North West')
    west       = (4, 'West')
    south_west = (5, 'South West')
    south_east = (6, 'South East')


class MapType(SuperEnum):
    __keys__ = ['id', 'title', 'colors']
    terran = (1, "Terran", TERRAIN_TERRAN)
    barren = (2, "Barren", TERRAIN_BARREN)
    gas = (3, "Gas", None)
    volcanic = (4, "Volcanic", TERRAIN_BARREN)
    oceanic = (5, "Oceanic", TERRAIN_OCEANIC)
    glacial = (6, "Barren", TERRAIN_BARREN)
