# Hexgen

## What is this?
It's a world map generator written in Python. It generates a random world map represented in a hexagon grid. The parameters for the generator allow for any kind of planet surface to be generated. It also can segment the surface into randomly sized globs called territories.

## Why?
I'm using this as a board for a browser-based game I am working on. It can be used for anything from DnD campaigns to open-source games or even just for fun.


## How to use

### Export types
The primary export of Hexgen is a data structure that represents the world map. It can also export a bunch of png files that show various features on the map.

One interesting thing it can do is take all the data about a hexagon and determine its true color. As exported as an image, the entire grid taken as a whole can be thought of as a satellite image.

### Hexagon types:
- land: defined as a solid surface
- water: define as a liquid surface

### Hexagon properties
- altitude (int, 0 - 255)
- temperature (celsius)
- moisture (int): water content
- fertility: soil fertility
- feature
    - lake
    - crater
    - volcano


### Parameters
- Required parameters
    - size (int): World map size in hexagons. This defines the width and height of the hexagon grid.
    - avg_temp (celsius): average surface temperature of this planet
- General parameters (required):
    - roughness (int, 0 - 10): used by the diamond-square algorithm to determine the roughness of the terrain.
    - axial_tilt (int, -90 - 90): This world's axial tilt. Has a huge impact on temperature variations.
    - land_percent (int, 0 - 100): Percent of surface that is land
    - hydrosphere (bool): whether the world has surface hydrosphere
    - ocean_type (OceanType): composition of the ocean. Can be water, hydrocarbons, magma

- Surface features (optional):
    - aquifer_max (int): maximum number of aquifers to place underground
    - river_max (int): maximum number of rivers to place on the map
    - crater_max (int): maximum number of craters to place on the surface
    - volcano_max (int): maximum number of volanoes to place on the surface
    - make_lakes (bool): Put lakes on hexes with 4 or more river segments

- Territories (optional):
    - make_territories (bool): whether to generate territories
    - land_only (bool): if True, territories will only exist on land
    - separate_zones (bool): if True, territories will never leave their zones
    - merge_islands (bool): if True, unclaimed islands will be given to the nearest territory
    - merge_small (bool): if True, small territories will be merged with their neighbors

- Exporting:
    - export_type (string, one of "png", "json")
    - png export:
        - draw_borders: (bool): Draw borders between territories and on coastlines
