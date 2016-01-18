import uuid


class RiverSegment:
    def __init__(self, grid, x, y, side, is_source=False):
        self.grid = grid
        self.x = x
        self.y = y
        self.side = side
        self.is_source = is_source
        self.next = None

        self.id = uuid.uuid4()

    @property
    def hex(self):
        return self.grid.find_hex(self.x, self.y)

    @property
    def edge(self):
        return self.hex.get_edge(self.side)

    def __repr__(self):
        return "<RiverSegment X: {}, Y: {}, side: {}>".format(self.x, self.y, self.side)

    @property
    def size(self):
        """
        Gets the size of the rest of the river
        :return: Number
        """
        count = 1
        river = self
        while river.next is not None:
            count += 1
            river = river.next
        return count

    def __eq__(self, other):
        """
        :param other: RiverSegment
        :return: True if both edges are equal
        """
        return self.edge == other.edge
