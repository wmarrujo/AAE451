import sys
sys.path.append("..")
from convert import convert
from parameters import *

mission = Mission()
mission.cruiseAltitude = convert(8000, "ft", "m")
mission.range = convert(700, "nmi", "m")
mission.passengers = 4
mission.loiter = convert(45, "min", "s")
mission.passengerWeight = convert(180, "lb", "N")
mission.baggageWeight = convert(80, "lb", "N")
mission.loiterAltitude = convert(3000, "ft", "m")

airplane = Airplane()
airplane.emptyWeight = convert(2250, "lb", "N")
airplane.maxGrossWeight = convert(3400, "lb", "N")
airplane.maxCruiseSpeed = convert(183, "kts", "m/s")

airplane.wing = Wing()
airplane.wing.sweep = convert(4, "deg", "rad") # FIXME: guessed
airplane.wing.span = convert(38.3, "ft", "m")
