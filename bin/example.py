from hexgen import generate
from hexgen.enums import MapType

options = {
    "map_type": MapType.terran,
    "surface_pressure": 1013.25,
    "axial_tilt": 23,
    "size": 100,
    "base_temp": -19.50,
    "avg_temp": 14,
    "sea_percent": 60,
    "hydrosphere": True,
    "num_rivers": 75,
    "num_territories": 0
}

gen = generate(options, image=True)
gen.export('bin/export.json')
