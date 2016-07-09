import uuid

class Geoform:
    """ A landmass or water feature """
    def __init__(self, hexes, geotype):
        self.type = geotype # GeoformType
        self.hexes = hexes # set
        self.size = len(hexes)
        self.id = uuid.uuid4() # uuid
        self.neighbors = set() # set
        self.to_delete = False

        for h in hexes:
            h.geoform = self

    def to_dict(self):
        """ Dictionary representation """
        return {
            "id": self.id.hex,
            "type": self.type.name,
            "size": self.size
        }

    def neighbor_of_type(self, other_type):
        """
            Returns all neighbors of a given type
        """
        result = []
        for n in self.neighbors:
            if n.type is other_type:
                result.append(n)
        return result

    def neighbor_of_types(self, other_types):
        result = []
        for t in other_types:
            result.extend(self.neighbor_of_type(t))
        return result

    def merge(self, other):
        """ Merge another Geoform into this one """
        # add their hexes to mine
        self.hexes.update(other.hexes)
        self.size += len(other.hexes)
        # set their hexes to me
        for h in other.hexes:
            h.geoform = self
        # empty their hexes
        other.hexes = set()
        other.size = 0
        # mark them to be deleted
        other.to_delete = True

    def is_geotype(self, geotype):
        """ Is this geoform this type? """
        return self.type is geotype

    def __eq__(self, other):
        return self.id == other.id

    def __key(self):
        return self.id

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        return "<Geoform: type: {}, size: {}, id: {}>".format(self.type.title, self.size, self.id)
