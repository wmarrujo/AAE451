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

#TECNAM MISSION

tecnamMission = Mission()
tecnamMission.passengers = 2
tecnamMission.pilots = 1

tecnamMission.segment["startup"]["altitude"] = 0
tecnamMission.segment["startup"]["thrustSetting"] = 0
tecnamMission.segment["startup"]["powerPercent"] = 0.1
tecnamMission.segment["startup"]["timeElapsed"] = convert(7, "min", "s")
tecnamMission.segment["startup"]["speed"] = convert(5, "kts", "m/s") # we know this to be true

tecnamMission.segment["takeoff"]["altitude"] = 0
tecnamMission.segment["takeoff"]["obstacle"] = convert(50, "ft" , "m")
tecnamMission.segment["takeoff"]["fieldLength"] = convert(2500,"ft","m")
tecnamMission.segment["takeoff"]["climbAngle"] = convert(3, "deg", "rad")
tecnamMission.segment["takeoff"]["powerPercent"] = 1
tecnamMission.segment["takeoff"]["timeElapsed"] = convert(3, "min", "s")
tecnamMission.segment["takeoff"]["speed"] = convert(100, "kts", "m/s") # FIXME: halfway between climb/cruise speed

tecnamMission.segment["climb"]["powerPercent"] = 1
tecnamMission.segment["climb"]["timeElapsed"] = convert(8, "min", "s") # FIXME: total guess, just needed to fill in field
tecnamMission.segment["climb"]["altitude"] = cruiseAltitude/2 # FIXME: this is a shit average
tecnamMission.segment["climb"]["speed"] = convert(140, "kts", "m/s") # FIXME: this is the minimum speed stipulated in the RFP

tecnamMission.segment["cruise"]["altitude"] = cruiseAltitude
tecnamMission.segment["cruise"]["powerPercent"] = 0.75 # tentative guess for now, will need a better estimate based on power available and required, which is a function of flight speed
tecnamMission.segment["cruise"]["speed"] = convert(140, "kts", "m/s") # FIXME: this is the minimum speed stipulated in the RFP
tecnamMission.segment["cruise"]["timeElapsed"] = convert(700, "nmi", "m")/tecnamMission.segment["cruise"]["speed"] # FIXME: solved from 13

tecnamMission.segment["descent"]["altitude"] = cruiseAltitude/2 # FIXME: this is a shit average
tecnamMission.segment["descent"]["powerPercent"] = 0
tecnamMission.segment["descent"]["timeElapsed"] = convert(10, "min", "s") # FIXME: "educated" guess based on the guessed climb time
tecnamMission.segment["descent"]["speed"] = convert(140, "kts", "m/s") # FIXME: this is the minimum speed stipulated in the RFP

tecnamMission.segment["abortClimb"]["timeElapsed"] = convert(4, "min", "s") # FIXME: guess
tecnamMission.segment["abortClimb"]["powerPercent"] = 1
tecnamMission.segment["abortClimb"]["altitude"] = loiterAltitude/2
tecnamMission.segment["abortClimb"]["speed"] = convert(90, "kts", "m/s") # FIXME: GUESSING CONTINUES

tecnamMission.segment["loiter"]["timeElapsed"] = convert(45, "min", "s") # stipulated in the RFP
tecnamMission.segment["loiter"]["powerPercent"] = 0.5 # FIXME: guess
tecnamMission.segment["loiter"]["altitude"] = loiterAltitude
tecnamMission.segment["loiter"]["speed"] = convert(100, "kts", "m/s") # FIXME: END ME this is a guess

tecnamMission.segment["abortDescent"]["timeElapsed"] = convert(6, "min", "s") # FIXME: guess
tecnamMission.segment["abortDescent"]["powerPercent"] = 0
tecnamMission.segment["abortDescent"]["altitude"] = loiterAltitude/2
tecnamMission.segment["abortDescent"]["speed"] = convert(100, "kts", "m/s") # FIXME: i'm gonna become addicted to guessing

tecnamMission.segment["landing"]["altitude"] = 0
tecnamMission.segment["landing"]["powerPercent"] = 1
tecnamMission.segment["landing"]["timeElapsed"] = convert(3, "min", "s")
tecnamMission.segment["landing"]["speed"] = convert(50, "kts", "m/s") # FIXME: Halfway between the guess value for abort descent

tecnamMission.segment["shutdown"]["altitude"] = 0
tecnamMission.segment["shutdown"]["powerPercent"] = 0.1
tecnamMission.segment["shutdown"]["timeElapsed"] = convert(7, "min", "s")
tecnamMission.segment["shutdown"]["speed"] = convert(5, "kts", "m/s") # we know this to be true


# DESIGN MISSION

designMission = Mission()
designMission.passengers = 5
designMission.pilots = 1

designSpeed = 180 # kts

designMission.segment["startup"]["thrustSetting"] = 0
designMission.segment["startup"]["powerPercent"] = 0.1
designMission.segment["startup"]["timeElapsed"] = convert(7, "min", "s")
designMission.segment["startup"]["speed"] = convert(5, "kts", "m/s") # we know this to be true

designMission.segment["takeoff"]["altitude"] = 0
designMission.segment["takeoff"]["obstacle"] = convert(50, "ft" , "m")
designMission.segment["takeoff"]["fieldLength"] = convert(2500,"ft","m")
designMission.segment["takeoff"]["climbAngle"] = convert(3, "deg", "rad")
designMission.segment["takeoff"]["powerPercent"] = 1
designMission.segment["takeoff"]["timeElapsed"] = convert(3, "min", "s")
designMission.segment["takeoff"]["speed"] = convert(100, "kts", "m/s") # FIXME: halfway between climb/cruise speed

designMission.segment["climb"]["powerPercent"] = 1
designMission.segment["climb"]["timeElapsed"] = convert(8, "min", "s") # FIXME: total guess, just needed to fill in field
designMission.segment["climb"]["altitude"] = cruiseAltitude/2 # FIXME: this is a shit average
designMission.segment["climb"]["speed"] = convert(designSpeed, "kts", "m/s") # FIXME: this is the minimum speed stipulated in the RFP

designMission.segment["cruise"]["altitude"] = cruiseAltitude
designMission.segment["cruise"]["powerPercent"] = 0.8 # tentative guess for now, will need a better estimate based on power available and required, which is a function of flight speed
designMission.segment["cruise"]["speed"] = convert(designSpeed, "kts", "m/s") # FIXME: this is the minimum speed stipulated in the RFP
designMission.segment["cruise"]["timeElapsed"] = convert(250, "nmi", "m")/designMission.segment["cruise"]["speed"] # FIXME: solved from 13

designMission.segment["descent"]["altitude"] = cruiseAltitude/2 # FIXME: this is a shit average
designMission.segment["descent"]["powerPercent"] = 0
designMission.segment["descent"]["timeElapsed"] = convert(10, "min", "s") # FIXME: "educated" guess based on the guessed climb time
designMission.segment["descent"]["speed"] = convert(designSpeed, "kts", "m/s") # FIXME: this is the minimum speed stipulated in the RFP

designMission.segment["abortClimb"]["timeElapsed"] = convert(4, "min", "s") # FIXME: guess
designMission.segment["abortClimb"]["powerPercent"] = 1
designMission.segment["abortClimb"]["altitude"] = loiterAltitude/2
designMission.segment["abortClimb"]["speed"] = convert(designSpeed/2, "kts", "m/s") # FIXME: GUESSING CONTINUES

designMission.segment["loiter"]["timeElapsed"] = convert(45, "min", "s") # stipulated in the RFP
designMission.segment["loiter"]["powerPercent"] = 0.5 # FIXME: guess
designMission.segment["loiter"]["altitude"] = loiterAltitude
designMission.segment["loiter"]["speed"] = convert(100, "kts", "m/s") # FIXME: END ME this is a guess

designMission.segment["abortDescent"]["timeElapsed"] = convert(6, "min", "s") # FIXME: guess
designMission.segment["abortDescent"]["powerPercent"] = 0
designMission.segment["abortDescent"]["altitude"] = loiterAltitude/2
designMission.segment["abortDescent"]["speed"] = convert(designSpeed/2, "kts", "m/s") # FIXME: i'm gonna become addicted to guessing

designMission.segment["landing"]["altitude"] = 0
designMission.segment["landing"]["powerPercent"] = 1
designMission.segment["landing"]["timeElapsed"] = convert(3, "min", "s")
designMission.segment["landing"]["speed"] = convert(designSpeed/2, "kts", "m/s") # FIXME: Halfway between the guess value for abort descent

designMission.segment["shutdown"]["altitude"] = 0
designMission.segment["shutdown"]["powerPercent"] = 0.1
designMission.segment["shutdown"]["timeElapsed"] = convert(7, "min", "s")
designMission.segment["shutdown"]["speed"] = convert(5, "kts", "m/s") # we know this to be true

# REFERENCE MISSION

referenceMission = Mission()
referenceMission.passengers = 3
referenceMission.pilots = 1

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
