import sys
sys.path.append("..")
from convert import convert # unit conversions
from stdatmo import * # standard atmospheric conditions
from scipy import * # math
from matplotlib.pyplot import * # plotting

from definitions import *
from parameters import *
from equations import *

################################################################################
# CONCEPT DEFINITION
################################################################################

tecnam = Airplane()
tecnam.etap = 0.8
tecnam.wingPlanform = convert(159.1, "ft^2", "m^2")
tecnam.wingSpan = convert(37.4, "ft", "m")
tecnam.takeoffWeight = convert(2717, "lb", "kg")
tecnam.emptyWeight = convert(1806, "lb", "kg")
tecnam.maxCruiseSpeed = convert(278, "km/hr", "kts")
tecnam.takeoffDistance = convert(1293, "ft", "m")
tecnam.landingDistance = convert(1145, "ft", "m")
tecnam.range = convert(1239, "km", "nmi")
tecnam.takeoffWeight = None # TODO: fill with weight for mission

################################################################################
# CALCULATIONS
################################################################################

# TODO: gross weight
takeoffWeight = TakeoffWeight(tecnam, designMission) # TODO: will need iteration
# TODO: landing distance
# TODO: takeoff distance
# TODO: range
# TODO: cost

print("takeoff weight = {0:.0f} lb\n".format(convert(takeoffWeight, "N", "lb")))