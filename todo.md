# Hexgen TODO / Wish List

- calendar
    [x] calendar split into months based on year and day length
    [ ] each planet has a calendar

- seasons
    [x] zones of latitude
    [ ] dependent on axial tilt and rotational period (day) and orbital period (year)
    [ ] each hex has metrics that are dependent on the month
    [ ] each hex may have different seasons
    [ ] a group of hexes that have a similar seasonal cycle make up a "seasonal zone"
- water cycle
    [x] ground water: aquifers
    [x] surface water: lakes and rivers
    [ ] seasonal rainfall
- wind
    http://imgarcade.com/1/prevailing[ ]wind[ ]direction-map/
    wind map winter: http://www.mapsofworld.com/world-maps/wind-and-pressure-jan-enlarge-map1.html
    wind map summer: http://www.mapsofworld.com/world-maps/wind-and-pressure-july-enlarge-map.html
    good pressure map: https://www.e-education.psu.edu/earth103/node/686

    [ ] each hex has a wind speed and hex direction
        [ ] wind speed: higher in ocean hexes than land hexes. Proportional to planet atmospheric pressure and average surface temperature
        [ ] wind direction: dependent on prevailing wind pattern
    [ ] calculating wind direction
        -  wind goes from high pressure to low pressure cells
        -  hex wind direction will point towards neighbor with lowest atmospheric pressure
        -  groups of similar pressure are "cells"
    [ ] calculating hex pressure
        - higher pressures on Tropic of Cancer (northern) and Tropic of Capricorn (southern) and polar regions
        - lower pressures on equator and between the tropics
        - lower pressure in higher elevations
        - dry air is more dense than moist air
        - cold air is more dense than warm air
    [ ] impact on rainfall: (ex: amazon rainforest)
        wind directed from an ocean hex onto a land hex = increase in moisture proportional to the change in elevation between this ocean hex and the land hex 5 hexes away in the same direction.
    [ ] impact on fertility
        wind from a desert area will increase fertility of land it reaches
    [ ] impact on temperature
        wind directed from an ocean hex onto a land hex increases its temperature and that of its inland neighbors proportional to the wind speed and latitude.
- ocean currents

- geography
    [ ] detect oceans
    [ ] detect inland seas
    [ ] detect lake systems
    [ ] detect mountain ranges
    [ ] detect glaciers
    [ ] detect peninsulas
    [ ] detect islands
    [ ] name all of the above
