from hexgen import generate
from hexgen.enums import MapType

options = {
    "map_type": MapType.volcanic,
    "size": 100,
    "avg_temp": 35,
    "sea_percent": 0,
    "hydrosphere": False,
    "num_rivers": 0,
    "num_territories": 0,
    "craters": True,
    "volcanoes": True
}

generate(options)
