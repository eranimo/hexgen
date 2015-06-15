import math
import random


class Heightmap:

    def __init__(self, params, debug=False):
        self.params = params

        # start making the heightmap
        self.size = params.get('size')
        self.grid = [[0 for x in range(0, self.size)] for x in range(0, self.size)]
        self.grid[0][0] = random.randint(0, 255)
        self.grid[self.size - 1][0] = random.randint(0, 255)
        self.grid[0][self.size - 1] = random.randint(0, 255)
        self.grid[self.size - 1][self.size - 1] = random.randint(0, 255)
        self._subdivide(0, 0, self.size - 1, self.size - 1)

        # compute average and record top height
        avg = []
        m = []
        for g in self.grid:
            m.append(max(g))
            avg.append(sum(g) / float(len(g)))

        self.top_height = max(m)
        self.average_height = sum(avg) / float(len(avg))
        sea_percent = params.get('sea_percent')
        self.sealevel = round(self.average_height * (sea_percent * 2 / 100))

        if sea_percent == 100:
            self.sealevel = 255

        if debug:
            print("Sea level at {} or {}%".format(self.sealevel, sea_percent))


    def height_at(self, x, y):
        return self.grid[x][y]

    def _adjust(self, xa, ya, x, y, xb, yb):
        """ fix the sides of the map """
        if self.grid[x][y] == 0:
            d = math.fabs(xa - xb) + math.fabs(ya - yb)
            ROUGHNESS = self.params.get('roughness')
            v = (self.grid[xa][ya] + self.grid[xb][yb]) / 2.0 \
                + (random.random() - 0.5) * d * ROUGHNESS
            c = int(math.fabs(v) % 257)
            if y == 0:
                self.grid[x][self.size - 1] = c
            if x == 0 or x == self.size - 1:
                if y < self.size - 1:
                    self.grid[x][self.size - 1 - y] = c
            range_low, range_high = self.params.get('height_range')
            if c < range_low:
                c = range_low
            elif c > range_high:
                c = range_high
            self.grid[x][y] = c

    def _subdivide(self, x1, y1, x2, y2):
        """ subdivide the heightmap iterate """
        if not ((x2 - x1 < 2.0) and (y2 - y1 < 2.0)):
            x = int((x1 + x2) / 2)
            y = int((y1 + y2) / 2)

            v = int((self.grid[x1][y1] + self.grid[x2][y1] +
                     self.grid[x2][y2] + self.grid[x1][y2]) / 4)
            range_low, range_high = self.params.get('height_range')
            if v < range_low:
                v = range_low
            elif v > range_high:
                v = range_high
            self.grid[x][y] = v

            self._adjust(x1, y1, x, y1, x2, y1)
            self._adjust(x2, y1, x2, y, x2, y2)
            self._adjust(x1, y2, x, y2, x2, y2)
            self._adjust(x1, y1, x1, y, x1, y2)

            self._subdivide(x1, y1, x, y)
            self._subdivide(x, y1, x2, y)
            self._subdivide(x, y, x2, y2)
            self._subdivide(x1, y, x, y2)
