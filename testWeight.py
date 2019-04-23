import sys
import os
hereDirectory = os.path.dirname(os.path.abspath(__file__))
rootDirectory = hereDirectory
sys.path.append(rootDirectory)

# LOCAL DEPENDENCIES

from utilities import *

from constants import *
from parameters import *
from missions import *
from equations import *
from sizing import *

sys.path.append(os.path.join(rootDirectory, "configurations"))
from diamond import defineAirplane as defineAirplaneObj

# EXTERNAL DEPENDENCIES

from matplotlib.pyplot import *
import cProfile

#####################478###########################################################
# TESTS
################################################################################
WS = convert(22.45, "lb/ft^2", "N/m^2") #14.66  17.06 22.45
PW = convert(0.0792, "hp/lb", "W/N") #0.0706  0.0727 0.0792
W0 = convert(3935 , "lb", "N") #2550 2771 3935
Wf = convert(478 , "lb", "N") #318 317 478
DPS = {"wing loading": WS, "power to weight ratio": PW, "initial gross weight": W0, "initial fuel weight": Wf}
# cProfile.run("PPs = getPerformanceParameters(airplaneName, DPS, designMission)")
airplane = defineAirplaneObj(DPS)
print("WDG: ", convert(W0, "N", "lb"), " lb")
print("Wf: ", convert(Wf, "N", "lb"), " lb")
print("Wpay (approx): ", convert(W0 - Wf - airplane.emptyMass*g, "N", "lb"), " lb")
print("EMPTY WEIGHT: ", convert(airplane.emptyMass * g, "N", "lb"), " lb")
print('WING WEIGHT ', convert(airplane.wing.mass * g, "N", "lb"), " lb")
print('FUESELAGE WEIGHT ', convert(airplane.fuselage.mass * g, "N", "lb"), " lb")
print('HORIZONTALSTABILIZER WEIGHT ', convert(airplane.horizontalStabilizer.mass * g, "N", "lb"), " lb")
print('VERTICALSTABILIZER WEIGHT ', convert(airplane.verticalStabilizer.mass * g, "N", "lb"), " lb")
print('ENGINEL WEIGHT ', convert(airplane.engines[0].mass * g, "N", "lb"), " lb")
print('ENGINER WEIGHT ', convert(airplane.engines[1].mass * g, "N", "lb"), " lb")
print('MAINGEAR WEIGHT ', convert(airplane.mainGear.mass * g, "N", "lb"), " lb")
print('FRONTGEAR WEIGHT ', convert(airplane.frontGear.mass * g, "N", "lb"), " lb")
print('FUELSYSTEM WEIGHT ', convert(airplane.fuelSystem.mass * g, "N", "lb"), " lb")
print('AVIONICS WEIGHT ', convert(airplane.avionics.mass * g, "N", "lb"), " lb")
print('FLIGHT CONTROLS WEIGHT ', convert(airplane.components[10].mass * g, "N", "lb"), " lb")
print('HYDRAULICS WEIGHT ', convert(airplane.components[11].mass * g, "N", "lb"), " lb")
print('ELECTRONICS WEIGHT ', convert(airplane.components[12].mass * g, "N", "lb"), " lb")
print('AIRCONICE WEIGHT ', convert(airplane.components[13].mass * g, "N", "lb"), " lb")
print('FURNISHINGS WEIGHT ', convert(airplane.components[14].mass * g, "N", "lb"), " lb")
