from app.generators.hexgen.hex import HexType, HexSide, HexFeature
from PIL import Image, ImageDraw
from app.generators.hexgen.constants import *

class HexGridDraw:
    """
    Draws a hexagon grid to an image. For debugging and development purposes
    """

    def __init__(self, grid, color_func, file_name, rivers=True,
                 numbers=False, show_coasts=False, borders=False):
        self.image = Image.new("RGB", (int(HEX_RECT_WIDTH * (grid.size + 0.6)),
                                       int((HEX_RECT_WIDTH) * grid.size)))
        self.draw = ImageDraw.Draw(self.image)
        self.Grid = grid
        self.color_func = color_func

        self.numbers = numbers
        self.show_coasts = show_coasts
        self.borders = borders

        for y in range(grid.size):
            for x in range(grid.size):
                hex = grid.grid[x][y]
                self.draw_hexagon(y * HEX_RECT_WIDTH + ((x % 2) * HEX_RADIUS),
                                  x * (SIDE_LENGTH + HEX_HEIGHT), x, y)

                if self.show_coasts and grid.has_water:
                    for e in hex.edges:
                        if hex.is_land and e.two.is_water:
                            self.draw_hex_edge(x, y, e.side, 4)
                if self.borders:
                    for e in hex.edges:
                        if e.one.is_owned and e.two.is_owned and \
                                        e.one.territory.id != e.two.territory.id:
                            self.draw_hex_edge(x, y, e.side, 2)
                if rivers:
                    cx = y * HEX_RECT_WIDTH + ( (x % 2) * HEX_RADIUS)
                    cy = x * (SIDE_LENGTH + HEX_HEIGHT)
                    origin = (cx + HEX_RADIUS, cy)
                    pointer = (cx + HEX_RECT_WIDTH, cy + HEX_HEIGHT)
                    pointer_2 = (cx + HEX_RECT_WIDTH, cy + HEX_HEIGHT + SIDE_LENGTH)
                    pointer_3 = (cx + HEX_RADIUS, cy + HEX_RECT_HEIGHT)
                    pointer_4 = (cx, cy + SIDE_LENGTH + HEX_HEIGHT)
                    pointer_5 = (cx, cy + HEX_HEIGHT)
                    segments = self.Grid.find_river(x, y)
                    river_blue = (21, 52, 60)  # (255, 255, 255)
                    for s in segments:
                        # print("RiverSegment {} at {}, {}".format(s, x, y))
                        if s is HexSide.north_east:
                            self.draw.line([origin, pointer], river_blue, width=3)
                        elif s is HexSide.east:
                            self.draw.line([pointer, pointer_2], river_blue, width=3)
                        elif s is HexSide.south_east:
                            self.draw.line([pointer_2, pointer_3], river_blue, width=3)
                        elif s is HexSide.south_west:
                            self.draw.line([pointer_3, pointer_4], river_blue, width=3)
                        elif s is HexSide.west:
                            self.draw.line([pointer_4, pointer_5], river_blue, width=3)
                        elif s is HexSide.north_west:
                            self.draw.line([pointer_5, origin], river_blue, width=3)

        print("Making ", file_name)
        self.image.save(file_name)

    def draw_hex_edge(self, x, y, side, width=3, color=(0, 0, 0)):
        s = side
        cx = y * HEX_RECT_WIDTH + ( (x % 2) * HEX_RADIUS)
        cy = x * (SIDE_LENGTH + HEX_HEIGHT)
        origin = (cx + HEX_RADIUS, cy)
        pointer = (cx + HEX_RECT_WIDTH, cy + HEX_HEIGHT)
        pointer_2 = (cx + HEX_RECT_WIDTH, cy + HEX_HEIGHT + SIDE_LENGTH)
        pointer_3 = (cx + HEX_RADIUS, cy + HEX_RECT_HEIGHT)
        pointer_4 = (cx, cy + SIDE_LENGTH + HEX_HEIGHT)
        pointer_5 = (cx, cy + HEX_HEIGHT)
        if s is HexSide.north_east:
            self.draw.line([origin, pointer], color, width=width)
        elif s is HexSide.east:
            self.draw.line([pointer, pointer_2], color, width=width)
        elif s is HexSide.south_east:
            self.draw.line([pointer_2, pointer_3], color, width=width)
        elif s is HexSide.south_west:
            self.draw.line([pointer_3, pointer_4], color, width=width)
        elif s is HexSide.west:
            self.draw.line([pointer_4, pointer_5], color, width=width)
        elif s is HexSide.north_west:
            self.draw.line([pointer_5, origin], color, width=width)

    def make_line(self, from_coord, to_coord):
        self.draw.line([from_coord, to_coord], (0, 0, 0))


    def draw_hexagon(self, cx, cy, x, y):
        origin = (cx + HEX_RADIUS, cy)
        pointer = (cx + HEX_RECT_WIDTH, cy + HEX_HEIGHT)
        pointer_2 = (cx + HEX_RECT_WIDTH, cy + HEX_HEIGHT + SIDE_LENGTH)
        pointer_3 = (cx + HEX_RADIUS, cy + HEX_RECT_HEIGHT)
        pointer_4 = (cx, cy + SIDE_LENGTH + HEX_HEIGHT)
        pointer_5 = (cx, cy + HEX_HEIGHT)

        hex = self.Grid.grid[x][y]
        self.draw.polygon([origin,
                           pointer,
                           pointer_2,
                           pointer_3,
                           pointer_4,
                           pointer_5],
                          outline=None,
                          fill=self.color_func(hex))

        self.make_line(origin, pointer)
        self.make_line(pointer, pointer_2)
        self.make_line(pointer_2, pointer_3)
        self.make_line(pointer_3, pointer_4)
        self.make_line(pointer_4, pointer_5)
        self.make_line(pointer_5, origin)

        if self.numbers:
            self.draw.text((cx + 10, cy + 3), str(hex.altitude), fill=(200, 200, 200))
            self.draw.text((cx + 4, cy + 11), str(x), fill=(200, 200, 200))
            self.draw.text((cx + 4, cy + 19), str(y), fill=(200, 200, 200))
            self.draw.text((cx + 18, cy + 11), str(hex.moisture), fill=(200, 200, 200))
            self.draw.text((cx + 18, cy + 19), str(hex.temperature), fill=(200, 200, 200))