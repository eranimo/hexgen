from hexgen import generate

options = {
    "size": 100,
    "avg_temp": 15,
    "sea_percent": 60,
    "hydrosphere": True,
    "num_rivers": 100,
    "num_territories": 50
}

generate(options)
