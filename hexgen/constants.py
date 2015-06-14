import math
from PIL import ImageColor

HEXAGON_ANGLE = 28 * math.pi / 180;  # 30 degrees
SIDE_LENGTH = 17
BOARD_WIDTH = 100;
BOARD_HEIGHT = BOARD_WIDTH;
HEX_HEIGHT = math.sin(HEXAGON_ANGLE) * SIDE_LENGTH
HEX_RADIUS = math.cos(HEXAGON_ANGLE) * SIDE_LENGTH
HEX_RECT_HEIGHT = SIDE_LENGTH + 2 * HEX_HEIGHT
HEX_RECT_WIDTH = 2 * HEX_RADIUS


WORLD_TYPE_HEIGHT_RANGES = {
    1: (0, 255), # terran
    2: (0, 255), # barren
    3: (0, 0),   # gas
    4: (0, 100), # volcanic
    5: (0, 255), # oceanic
    6: (0, 100)  # glacial
}


# in degrees celsius
# http://jsfiddle.net/4g5zfaqu/1/
TEMPERATURE_COLORS = [
    (-270, (110, 110, 90)),
    (-260, (115, 120, 100)),
    (-250, (120, 130, 110)),
    (-240, (135, 140, 120)),
    (-230, (140, 150, 130)),
    (-220, (145, 160, 150)),
    (-210, (150, 170, 170)),
    (-200, (155, 180, 190)),
    (-190, (160, 190, 210)),
    (-180, (165, 200, 230)),
    (-170, (170, 210, 250)),
    (-160, (165, 200, 240)),
    (-150, (160, 190, 230)),
    (-140, (155, 180, 220)),
    (-130, (140, 170, 220)),
    (-120, (135, 150, 220)),
    (-110, (130, 130, 220)),
    (-100, (130, 100, 220)),
    (-90,  (140, 60, 230)),
    (-80,  (150, 30, 240)),
    (-70,  (160, 0, 260)),
    (-60,  (120, 0, 220)),
    (-50,  (80, 0, 190)),
    (-40,  (0, 0, 156)),
    (-35, (0, 0, 208)),
    (-30, (0, 0, 255)),
    (-25, (0, 97, 255)),
    (-20, (0, 155, 255)),
    (-15, (0, 203, 255)),
    (-10, (21, 255, 255)),
    (-5,  (149, 255, 255)),
    (0,   (202, 255, 255)),
    (5,   (255, 255, 147)),
    (10,  (255, 255, 0)),
    (15,  (255, 205, 0)),
    (20,  (255, 154, 0)),
    (25,  (255, 102, 0)),
    (30,  (206, 50, 0)),
    (35,  (154, 0, 0)),
    (40,  (133, 0, 0)),
    (80,  (123, 0, 0)),
    (80,  (113, 0, 0)),
    (100,  (100, 0, 0)),
    (120,  (90, 0, 0)),
    (140,  (80, 0, 0))
]

# at or below these altitudes
TERRAIN_TERRAN = [
    (-25, (0, 15, 120)),
    (-15, (0, 20, 130)),
    (0,   (0, 20, 170)),
    (20,  (56, 89, 22)),
    (50,  (75, 112, 9)),
    (75,  (129, 135, 42)),
    (100, (196, 150, 95)),
    (110, (223, 190, 144)),
    (120, (233, 200, 154)),
    (135, (243, 210, 164)),
    (140, (253, 220, 174))
]

TERRAN_OCEAN_SATELLITE = [
    (-20, [(21, 51, 62), (20, 50, 61), (22, 52, 63)]),
    (-10, [(21, 61, 72), (20, 60, 71), (22, 62, 73)]),
    (0, [(31, 72, 80), (29, 70, 82), (33, 73, 79)])
]

# http://jsfiddle.net/n75wktdk/1/
TERRAIN_OCEANIC = [
    (-220, ImageColor.getrgb("hsl(233, 100%, 10%)")),
    (-200, ImageColor.getrgb("hsl(233, 100%, 15%)")),
    (-180, ImageColor.getrgb("hsl(233, 100%, 20%)")),
    (-160, ImageColor.getrgb("hsl(233, 100%, 25%)")),
    (-140, ImageColor.getrgb("hsl(233, 90%, 30%)")),
    (-120, ImageColor.getrgb("hsl(233, 90%, 35%)")),
    (-100, ImageColor.getrgb("hsl(233, 80%, 40%)")),
    (-80,  ImageColor.getrgb("hsl(233, 80%, 45%)")),
    (-60,  ImageColor.getrgb("hsl(233, 70%, 50%)")),
    (-40,  ImageColor.getrgb("hsl(230, 70%, 55%)")),
    (-20,  ImageColor.getrgb("hsl(228, 70%, 60%)")),
    (0,    ImageColor.getrgb("hsl(224, 70%, 65%)"))
]

# http://jsfiddle.net/vm2mkpza/3/
TERRAIN_BARREN = [
    (-60, ImageColor.getrgb("hsl(230, 80%, 20%)")),
    (-45, ImageColor.getrgb("hsl(230, 80%, 25%)")),
    (-30, ImageColor.getrgb("hsl(230, 80%, 30%)")),
    (-15, ImageColor.getrgb("hsl(230, 80%, 35%)")),
    (0,   ImageColor.getrgb("hsl(230, 80%, 40%)")),
    (20,  ImageColor.getrgb("hsl(35, 30%, 50%)")),
    (50,  ImageColor.getrgb("hsl(35, 35%, 53%)")),
    (75,  ImageColor.getrgb("hsl(35, 40%, 56%)")),
    (100, ImageColor.getrgb("hsl(35, 45%, 60%)")),
    (110, ImageColor.getrgb("hsl(35, 50%, 63%)")),
    (120, ImageColor.getrgb("hsl(35, 55%, 66%)")),
    (135, ImageColor.getrgb("hsl(35, 60%, 70%)")),
    (140, ImageColor.getrgb("hsl(35, 65%, 73%)")),
    (160, ImageColor.getrgb("hsl(35, 70%, 76%)")),
    (180, ImageColor.getrgb("hsl(35, 75%, 80%)")),
    (200, ImageColor.getrgb("hsl(35, 80%, 83%)")),
    (220, ImageColor.getrgb("hsl(35, 80%, 86%)"))
]

# http://jsfiddle.net/bft01aza/
DUSTY_BARREN_SATELLITE = [
    (20,  ImageColor.getrgb("hsl(13, 34%, 21%)")),
    (50,  ImageColor.getrgb("hsl(14, 34%, 25%)")),
    (75,  ImageColor.getrgb("hsl(14, 40%, 30%)")),
    (100, ImageColor.getrgb("hsl(15, 42%, 35%)")),
    (110, ImageColor.getrgb("hsl(15, 43%, 38%)")),
    (120, ImageColor.getrgb("hsl(16, 43%, 40%)")),
    (135, ImageColor.getrgb("hsl(17, 43%, 42%)")),
    (140, ImageColor.getrgb("hsl(17, 43%, 45%)")),
    (160, ImageColor.getrgb("hsl(15, 42%, 47%)")),
    (180, ImageColor.getrgb("hsl(14, 45%, 50%)")),
    (200, ImageColor.getrgb("hsl(13, 51%, 55%)")),
    (220, ImageColor.getrgb("hsl(13, 61%, 61%)"))
]
# http://jsfiddle.net/kp0m6b5s/
BARREN_WET = [
    (20,  ImageColor.getrgb("hsl(15, 24%, 21%)")),
    (50,  ImageColor.getrgb("hsl(15, 24%, 25%)")),
    (75,  ImageColor.getrgb("hsl(15, 20%, 30%)")),
    (100, ImageColor.getrgb("hsl(15, 22%, 35%)")),
    (110, ImageColor.getrgb("hsl(15, 23%, 38%)")),
    (120, ImageColor.getrgb("hsl(15, 23%, 40%)")),
    (135, ImageColor.getrgb("hsl(15, 23%, 42%)")),
    (140, ImageColor.getrgb("hsl(15, 23%, 45%)")),
    (160, ImageColor.getrgb("hsl(15, 22%, 47%)")),
    (180, ImageColor.getrgb("hsl(15, 22%, 50%)")),
    (200, ImageColor.getrgb("hsl(15, 23%, 55%)")),
    (220, ImageColor.getrgb("hsl(15, 23%, 61%)"))
]



# http://jsfiddle.net/mwn7c4k4/2/
BARREN_SATELLITE = [
    (20,  ImageColor.getrgb("hsl(13, 8%, 21%)")),
    (50,  ImageColor.getrgb("hsl(14, 8%, 25%)")),
    (75,  ImageColor.getrgb("hsl(14, 8%, 30%)")),
    (100, ImageColor.getrgb("hsl(15, 8%, 35%)")),
    (110, ImageColor.getrgb("hsl(15, 8%, 38%)")),
    (120, ImageColor.getrgb("hsl(16, 8%, 40%)")),
    (135, ImageColor.getrgb("hsl(17, 8%, 42%)")),
    (140, ImageColor.getrgb("hsl(17, 8%, 45%)")),
    (160, ImageColor.getrgb("hsl(15, 8%, 47%)")),
    (180, ImageColor.getrgb("hsl(14, 8%, 50%)")),
    (200, ImageColor.getrgb("hsl(13, 8%, 55%)")),
    (220, ImageColor.getrgb("hsl(13, 8%, 61%)"))
]

# http://jsfiddle.net/sw6hakz2/
GLACIAL_SATELLITE = [
    (-10, (ImageColor.getrgb("hsl(200, 48%, 30%)"))),
    (0,   (ImageColor.getrgb("hsl(200, 48%, 35%)"))),
    (10,  (ImageColor.getrgb("hsl(222, 14%, 65%)"))),
    (20,  (ImageColor.getrgb("hsl(222, 14%, 70%)"))),
    (30,  (ImageColor.getrgb("hsl(222, 14%, 75%)"))),
    (50,  (ImageColor.getrgb("hsl(222, 14%, 80%)"))),
    (90,  (ImageColor.getrgb("hsl(222, 14%, 83%)")))
]


#
VOLCANIC_SATELLITE = [
    (65,  ImageColor.getrgb("hsl(13, 22%, 17%)")),
    (70,  ImageColor.getrgb("hsl(13, 22%, 20%)")),
    (80,  ImageColor.getrgb("hsl(13, 22%, 23%)")),
    (90,  ImageColor.getrgb("hsl(13, 22%, 25%)")),
    (100, ImageColor.getrgb("hsl(13, 22%, 27%)")),
    (110, ImageColor.getrgb("hsl(13, 22%, 30%)")),
    (120, ImageColor.getrgb("hsl(13, 22%, 32%)")),
    (130, ImageColor.getrgb("hsl(13, 22%, 35%)")),
    (135, ImageColor.getrgb("hsl(13, 22%, 37%)")),
    (140, ImageColor.getrgb("hsl(13, 22%, 39%)")),
    (150, ImageColor.getrgb("hsl(13, 22%, 41%)")),
    (155, ImageColor.getrgb("hsl(13, 22%, 43%)"))
]

VOLCANIC_LIQUID = [
    (217, 0, 0),
    (225, 0, 0),
    (200, 5, 5),
]
