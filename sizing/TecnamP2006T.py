import sys
sys.path.insert(0, sys.path[0] + "/../")
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
tecnam.takeoffWeight = convert(2717, "lb", "N")
tecnam.emptyWeight = convert(1806, "lb", "N")
tecnam.maxCruiseSpeed = convert(278, "km/hr", "kts")
tecnam.takeoffDistance = convert(1293, "ft", "m")
tecnam.landingDistance = convert(1145, "ft", "m")
tecnam.range = convert(1239, "km", "nmi")
tecnam.takeoffWeight = 1230*g # TODO: fill with weight for mission
tecnam.maxPowerToWeight = convert(73.5*2, "kW", "W") / (1230*g) # from constraint diagrams
tecnam.powerplant = Powerplant()
tecnam.powerplant.percentEnergyFromBattery = 0
tecnam.wingLoading = 78 * g
tecnam.components = [
    Fuselage(1, 1.5, 8.7), # from POH
    Nacelle(1, 0.8, 1.6),
    Nacelle(1, 0.8, 1.6),
    Surface(1, 14.76, 0.15/1.295, 11.40), # First set is the actual wings
    Surface(1.05, 3.3*0.8, 0.1/0.8, 3.3), # Second set is the horizontal stabilizer
    Surface(1.05, 1.58*1, 0.1, 1.58)] # Third set is the vertical stabilizer
tecnam.miscellaneousParasiteDragFactor = 0.1 # TODO: correction factor?

################################################################################
# CALCULATIONS
################################################################################

# TODO: gross weight
oldWeight = 0
iteration = 0
while abs(oldWeight - tecnam.takeoffWeight) > 1:
    oldWeight = tecnam.takeoffWeight
    tecnam.takeoffWeight = TakeoffWeight(tecnam, tecnamMission)
    
    print("Takeoff Weight = ", convert(tecnam.takeoffWeight, "N", "lb"))
    if iteration > 1000:
        print(convert(tecnam.takeoffWeight, "N", "lb"))
        raise ValueError("Maximum Iterations Reached, stopping iterations")
    iteration += 1
print(iteration)
# TODO: landing distance
#landingDistance = LandingDistance(tecnam, designMission)
# TODO: takeoff distance
# TODO: range
# TODO: cost
# TODO: drag buildup
parasiteDrags = zip(Mission.segments, [ParasiteDrag(tecnam, designMission, segment) for segment in Mission.segments])

print("takeoff weight = {0:.0f} lb".format(convert(tecnam.takeoffWeight, "N", "lb")))
#print("landing distance = {0:.0f} lb\n".format(convert(takeoffWeight, "m", "ft")))
for (segment, parasiteDrag) in parasiteDrags:
    print("segment {0:12}, parasite drag = {1:.4f}".format(segment, parasiteDrag))
