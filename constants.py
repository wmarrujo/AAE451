from parameters import *
from convert import convert
from stdatmo import *

################################################################################
# FUNDAMENTAL CONSTANTS
################################################################################

g = 9.80665 # m/s² # gravitational acceleration
rho0 = densityAtAltitude(0) # density at sea level

################################################################################
# GLOBAL CONSTANTS
################################################################################

avgasEnergyDensity = convert(44.65, "MJ/kg", "J/kg")
batteryEnergyDensity = convert(265, "Wh/kg", "J/kg")
avgasDensity = convert(0.721, "kg/L", "kg/m^3")

################################################################################
# USE CASE CONSTANTS
################################################################################

heavyPassengerWeight = convert(180, "lb", "N") # weight of a heavy passenger
lightPassengerWeight = convert(175, "lb", "N") # weight of a light passenger
heavyPassengerBagWeight = convert(30, "lb", "N") # weight of bag of a heavy passenger
lightPassengerBagWeight = convert(25, "lb", "N") # weight of bag of a light passenger
pilotWeight = convert(180, "lb", "N") # weight of a pilot
obstacleHeight = convert(50, "ft", "m") # height of obstacle at end of runway
cruiseAltitude = convert(8000, "ft", "m")
loiterAltitude = convert(3000, "ft", "m")
loiterTime = convert(45, "min", "s")
shaftEfficiency = 0.99 # 
electricalSystemEfficiency = 0.98 # 
internalCombustionMotorEfficiency = 0.4 # 
electricalMotorEfficiency = 0.98 # 
engineLapseRateCoefficient = 0.7 # 