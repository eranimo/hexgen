from hexgen import generate
from hexgen.enums import MapType

options = {
    "map_type": MapType.terran,
    "size": 100,
    "base_temp": 0,
    "avg_temp": 15,
    "sea_percent": 60,
    "hydrosphere": True,
    "num_rivers": 50,
    "num_territories": 50
}

generate(options)
