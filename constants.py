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
timeCap = convert(5, "hr", "s")

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

################################################################################
# COST SPECIFIC CONSTANTS
################################################################################

inflation2012to2019 = 1.1 # 1USD in 2012 equals 1.1USD in 2019

# Acquisition Cost

numberFlightTestAircraft = 4  # number [planes] : (2 <= x <= 6)  # Raymer v6 18.4.2
certFudge = 1 # for FAR Part 23
flapFudge = 1 # for simple flap system
pressFudge = 1 # for unpressurized aircraft
taperFudge = 0.95 # for no taper
engineeringLaborRate = 92 # [2012 USD/hr]
toolingLaborRate = 61 # [2012 USD/hr]
manufacturingLaborRate = 53 # [2012 USD/hr]
numberICEngines = 2 # This is only for all IC engine configuration
avionicPrice = 20000 # [2019 USD] Based on value from Blue Skies Aviation
cabinHeaterPrice = 5800 # [2019 USD] Based on average values for Cessna and Beechcraft aircraft of our size
seatPrice = 500 # [2019 USD] OregonAero pricing average for fixed wing GA aircraft seats
manufacturerLiabilityInsurance = 55000 # [2019 USD]  From Gudmundson's suggestion

# Operating Cost

maintF = 0 # 0 for maintenance done by A&P mechanic, -0.15 for done by owner
engineF = 0 # 0 for easy engine access, 0.02 for hard
VFRF = 0.02 # 0.02 for VFR radios, 0 for no VFR radios
IFRF = 0.04 # 0.04 for IFR radios, 0 for no IFR radios
fuelF = 0 # 0 for non-integral fuel tanks, 0.01 for integral
flapF = 0 # 0 for simple flap system, 0.02 for complex
certF = 0 # for 14 CRF part 23
flightHoursYear = 780 # 20 times a week, 45 min flight time, for 52 weeks
APmechRate = 60 # [2012 USD/hr]
monthlyStorageRate = 250 # [2012 USD/month]
fuelRate = 5 # [2019 USD/gal]
electricityRate = 0.10 # From RFP [2019 USD/ KW-hr]
pilotRate = 100 # [2012 USD/hr]
inspectionCost = 2000 # [2019 USD/year] # average from Blue Skies gravitational

################################################################################
# RFP Constraints
################################################################################

minimumTakeoffFieldLength = convert(1500, "ft", "m")
minimumRange = convert(300, "nmi", "m")
maximumFlightTime = convert(1.5, "hr", "s")
