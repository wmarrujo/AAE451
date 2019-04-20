# LOCAL DEPENDENCIES

from utilities import *

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
# SIMULATION
################################################################################

timestep = 1 # s
iterationCap = 100000
timeCap = convert(10, "hr", "s")

################################################################################
# AIRPLANE
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
runwayFrictionCoefficientNoBrakes = 0.03 # 0.015-0.04 -> from Raymer Table 17.1
runwayFrictionCoefficientWithBrakes = 0.5 # 0.3-0.6 -> from Raymer Table 17.1
inflation2012to2019 = 1.1 # 1USD in 2012 equals 1.1USD in 2019
engineeringWrapRate = 115 # [2012 USD]
toolingWrapRate = 118 # [2012 USD]
qualityControlWrapRate = 108 # [2012 USD]
manufacturingWrapRate = 98 # [2012 USD]
generalAviationPassengerCostFactor = 850 # [2012 USD]

################################################################################
# RFP Constraints
################################################################################

minimumTakeoffFieldLength = convert(2500, "ft", "m")
minimumRange = convert(250, "nmi", "m")
referenceRange = convert(135, "nmi", "m")
maximumFlightTime = convert(1.5, "hr", "s")
