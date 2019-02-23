from parameters import *
from convert import convert

################################################################################
# CONSTANTS
################################################################################

g = 9.80665 # m/s² # Gravitational Acceleration
heavyPassengerWeight = convert(180, "lb", "N") # weight of a heavy passenger
lightPassengerWeight = convert(175, "lb", "N") # weight of a light passenger
heavyPassengerBagWeight = convert(25, "lb", "N") # weight of bag of a heavy passenger
lightPassengerBagWeight = convert(25, "lb", "N") # weight of bag of a light passenger
pilotWeight = convert(180, "lb", "N") # weight of a pilot
takeoffObstacle = convert(50, "ft", "m") # height of obstacle at end of runway

################################################################################
# MISSION
################################################################################

designMission = Mission()
designMission.passengers = 4
designMission.pilots = 1
designMission.segment["startup"]["altitude"] = 0
designMission.segment["startup"]["weightFraction"] = 0.95
designMission.segment["cruise"]["altitude"] = convert(8000, "ft", "m")

referenceMission = Mission()
referenceMission.passengers = 6
referenceMission.pilots = 1
referenceMission.segment["startup"]["altitude"] = 0
referenceMission.segment["takeoff"]["altitude"] = 0

################################################################################
# COMPONENTS
################################################################################

# TODO: insert propeller 