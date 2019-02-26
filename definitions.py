from parameters import *
from convert import convert

################################################################################
# CONSTANTS
################################################################################

g = 9.80665 # m/s² # Gravitational Acceleration
heavyPassengerWeight = convert(180, "lb", "N") # weight of a heavy passenger
lightPassengerWeight = convert(175, "lb", "N") # weight of a light passenger
heavyPassengerBagWeight = convert(30, "lb", "N") # weight of bag of a heavy passenger
lightPassengerBagWeight = convert(25, "lb", "N") # weight of bag of a light passenger
pilotWeight = convert(180, "lb", "N") # weight of a pilot
takeoffObstacle = convert(50, "ft", "m") # height of obstacle at end of runway
cruiseAltitude = 4300 #convert(8000, "ft", "m")
loiterAltitude = convert(3000, "ft", "m")
avgasEnergyDensity = convert(44.65, "MJ/kg", "J/kg")
batteryEnergyDensity = convert(265, "Wh/kg", "J/kg")
shaftEfficiency = 0.99
electricalSystemEfficiency = 0.98
internalCombustionMotorEfficiency = 0.4
electricalMotorEfficiency = 0.98
engineLapseRateCoefficient = 0.7
avgasDensity = 0.721 # kg/L

################################################################################
# MISSION
################################################################################

# DESIGN MISSION

designMission = Mission()
designMission.passengers = 4
designMission.pilots = 1

designMission.segment["startup"]["altitude"] = 0
designMission.segment["startup"]["weightFraction"] = 0.95

designMission.segment["takeoff"]["altitude"] = 0


designMission.segment["cruise"]["altitude"] = cruiseAltitude

# REFERENCE MISSION

referenceMission = Mission()
referenceMission.passengers = 6
referenceMission.pilots = 1

referenceMission.segment["startup"]["altitude"] = 0
referenceMission.segment["startup"]["thrustSetting"] = 0
referenceMission.segment["startup"]["powerPercent"] = 0.1
referenceMission.segment["startup"]["timeElapsed"] = convert(7, "min", "s")
referenceMission.segment["startup"]["speed"] = convert(5, "kts", "m/s") # we know this to be true

referenceMission.segment["takeoff"]["altitude"] = 0
referenceMission.segment["takeoff"]["obstacle"] = convert(50, "ft" , "m")
referenceMission.segment["takeoff"]["fieldLength"] = convert(2500,"ft","m")
referenceMission.segment["takeoff"]["climbAngle"] = convert(3, "deg", "rad")
referenceMission.segment["takeoff"]["powerPercent"] = 1
referenceMission.segment["takeoff"]["timeElapsed"] = convert(3, "min", "s")
referenceMission.segment["takeoff"]["speed"] = convert(100, "kts", "m/s") # FIXME: halfway between climb/cruise speed

referenceMission.segment["climb"]["powerPercent"] = 1
referenceMission.segment["climb"]["timeElapsed"] = convert(8, "min", "s") # FIXME: total guess, just needed to fill in field
referenceMission.segment["climb"]["altitude"] = cruiseAltitude/2 # FIXME: this is a shit average
referenceMission.segment["climb"]["speed"] = convert(190, "kts", "m/s") # FIXME: this is the minimum speed stipulated in the RFP

referenceMission.segment["cruise"]["altitude"] = cruiseAltitude
referenceMission.segment["cruise"]["powerPercent"] = 0.8 # tentative guess for now, will need a better estimate based on power available and required, which is a function of flight speed
referenceMission.segment["cruise"]["speed"] = convert(190, "kts", "m/s") # FIXME: this is the minimum speed stipulated in the RFP
referenceMission.segment["cruise"]["timeElapsed"] = convert(135, "nmi", "m")/referenceMission.segment["cruise"]["speed"] - convert(8+10, "min", "s") # FIXME: solved from 13

referenceMission.segment["descent"]["altitude"] = cruiseAltitude/2 # FIXME: this is a shit average
referenceMission.segment["descent"]["powerPercent"] = 0
referenceMission.segment["descent"]["timeElapsed"] = convert(10, "min", "s") # FIXME: "educated" guess based on the guessed climb time
referenceMission.segment["descent"]["speed"] = convert(190, "kts", "m/s") # FIXME: this is the minimum speed stipulated in the RFP

referenceMission.segment["abortClimb"]["timeElapsed"] = convert(4, "min", "s") # FIXME: guess
referenceMission.segment["abortClimb"]["powerPercent"] = 1
referenceMission.segment["abortClimb"]["altitude"] = loiterAltitude/2
referenceMission.segment["abortClimb"]["speed"] = convert(100, "kts", "m/s") # FIXME: GUESSING CONTINUES

referenceMission.segment["loiter"]["timeElapsed"] = convert(45, "min", "s") # stipulated in the RFP
referenceMission.segment["loiter"]["powerPercent"] = 0.5 # FIXME: guess
referenceMission.segment["loiter"]["altitude"] = loiterAltitude
referenceMission.segment["loiter"]["speed"] = convert(100, "kts", "m/s") # FIXME: END ME this is a guess

referenceMission.segment["abortDescent"]["timeElapsed"] = convert(6, "min", "s") # FIXME: guess
referenceMission.segment["abortDescent"]["powerPercent"] = 0
referenceMission.segment["abortDescent"]["altitude"] = loiterAltitude/2
referenceMission.segment["abortDescent"]["speed"] = convert(100, "kts", "m/s") # FIXME: i'm gonna become addicted to guessing

referenceMission.segment["landing"]["altitude"] = 0
referenceMission.segment["landing"]["powerPercent"] = 1
referenceMission.segment["landing"]["timeElapsed"] = convert(3, "min", "s")
referenceMission.segment["landing"]["speed"] = convert(50, "kts", "m/s") # FIXME: Halfway between the guess value for abort descent

referenceMission.segment["shutdown"]["altitude"] = 0
referenceMission.segment["shutdown"]["powerPercent"] = 0.1
referenceMission.segment["shutdown"]["timeElapsed"] = convert(7, "min", "s")
referenceMission.segment["shutdown"]["speed"] = convert(5, "kts", "m/s") # we know this to be true

################################################################################
# COMPONENTS
################################################################################
