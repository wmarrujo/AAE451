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
cruiseAltitude = convert(8000, "ft", "m")
avgasEnergyDensity = convert(44.65, "MJ/kg", "J/kg")
batteryEnergyDensity = convert(265, "Wh/kg", "J/kg")
shaftEfficiency = 0.99
electricalSystemEfficiency = 0.98
internalCombustionMotorEfficiency = 0.4
electricalMotorEfficiency = 0.98

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
referenceMission.segment["startup"]["timeElapsed"] = 7*60

referenceMission.segment["takeoff"]["altitude"] = 0
referenceMission.segment["takeoff"]["obstacle"] = convert(50, "ft" , "m")
referenceMission.segment["takeoff"]["fieldLength"] = convert(2500,"ft","m")
referenceMission.segment["takeoff"]["climbAngle"] = convert(3, "deg", "rad")
referenceMission.segment["takeoff"]["powerPercent"] = 1
referenceMission.segment["takeoff"]["timeElapsed"] = 3*60

referenceMission.segment["climb"]["powerPercent"] = 1
referenceMission.segment["climb"]["timeElapsed"] = 8*60 # total guess, just needed to fill in field

referenceMission.segment["cruise"]["altitude"] = cruiseAltitude
referenceMission.segment["cruise"]["powerPercent"] = 0.8 # tentative guess for now, will need a better estimate based on power available and required, which is a function of flight speed
referenceMission.segment["cruise"]["timeElapsed"] = (45-8-10)*60 # solved from the other time guesses

referenceMission.segment["descent"]
referenceMission.segment["descent"]["powerPercent"] = 0
referenceMission.segment["descent"]["timeElapsed"] = 10*60 # "educated" guess based on the guessed climb time

referenceMission.segment["abortClimb"]["timeElapsed"] = 4*60 # still guessing
referenceMission.segment["abortClimb"]["powerPercent"] = 1


referenceMission.segment["loiter"]["timeElapsed"] = 45*60 # stipulated in the RFP
referenceMission.segment["loiter"]["powerPercent"] = 0.5 # tentative guess for now, see above

referenceMission.segment["abortDescent"]["timeElapsed"] = 6*60 # finally done guessing
referenceMission.segment["abortDescent"]["powerPercent"] = 0

referenceMission.segment["landing"]["altitude"] = 0
referenceMission.segment["landing"]["powerPercent"] = 1
referenceMission.segment["landing"]["timeElapsed"] = 3*60

referenceMission.segment["shutdown"]["altitude"] = 0
referenceMission.segment["shutdown"]["powerPercent"] = 0.1
referenceMission.segment["shutdown"]["timeElapsed"] = 7*60

################################################################################
# COMPONENTS
################################################################################

hybridParallel = Powerplant()
hybridParallel.fuelUsedForEnergyUsed = _hybridparallelFuelUsed

def _hybridParallelFuelUsed(missionSegment, energyUsed):
    pass

hybridSeries = Powerplant()
hybridSeries.etaf = internalCombustionMotorEfficiency * electricalSystemEfficiency**2 * shaftEfficiency * hybridSeries.propeller.eta
hybridSeries.etab = electricalSystemEfficiency * shaftEfficiency * hybridSeries.propeller.eta
hybridSeries.fuelUsedForEnergyUsed = _hybridseriesFuelUsed

def _hybridseriesFuelUsed(missionSegment, energyUsed):
    
    batteryEnergyUsed = energyUsed / hybridSeries.etab
    
    return
    
electric = Powerplant()
electric.eta = electricalSystemEfficiency * shaftEfficiency * electric.propeller.eta
electric.fuelUsedForEnergyUsed = _electricFuelUsed

def _electricFuelUsed(missionSegment, energyUsed):
    batteryEnergyUsed = energyUsed / electric.eta
    return (batteryEnergyUsed / batteryEnergyDensity) * g
        
conventional = Powerplant()
conventional.eta = internalCombustionMotorEfficiency * shaftEfficiency * conventional.propeller.eta
conventional.fuelUsedForEnergyUsed = _conventionalFuelUsed

def _conventionalFuelUsed(missionSegment, energyUsed):
    fuelEnergyUsed = energyUsed / conventional.eta
    return (fuelEnergyUsed / avgasEnergyDensity) * g


genericPropeller = Propeller()
genericPropeller.eta = 0.8
