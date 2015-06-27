from hexgen import generate
from hexgen.enums import MapType

options = {
    "map_type": MapType.terran,
    "surface_pressure": 1013.25,
    "axial_tilt": -23,
    "size": 100,
    "base_temp": -20,
    "avg_temp": 8,
    "sea_percent": 60,
    "hydrosphere": True,
    "num_rivers": 0,
    "num_territories": 0
}

generate(options)
