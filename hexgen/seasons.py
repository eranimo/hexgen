from hexgen.enums import SuperEnum

class Unit:
    class Temperature(SuperEnum):
        celsius = (3, 'Celsius', 'C')
        fahrenheit= (3, 'Fahrenheit', 'F')


class SeasonalValue:

    def __init__(self, summer, winter, unit):
        self.unit = unit
        self.summer = summer
        self.winter = winter


val = SeasonalValue(30, 90, Unit.Temperature.celsius)
