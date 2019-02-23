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
designMission.segment["startup"]["time"] = 10*60 # 10 minutes into seconds

designMission.segment["takeoff"]["altitude"] = 0


designMission.segment["cruise"]["altitude"] = cruiseAltitude

# REFERENCE MISSION

referenceMission = Mission()
referenceMission.passengers = 6
referenceMission.pilots = 1

referenceMission.segment["startup"]["altitude"] = 0
referenceMission.segment["startup"]["thrustSetting"] = 0
referenceMission.segment["startup"]["time"] = 10*60 # 10 minutes into seconds

referenceMission.segment["takeoff"]["altitude"] = 0
referenceMission.segment["takeoff"]["obstacle"] = convert(50, "ft" , "m")
referenceMission.segment["takeoff"]["fieldLength"] = convert(2500,"ft","m")
referenceMission.segment["takeoff"]["climbAngle"] = convert(3, "deg", "rad")

referenceMission.segment["cruise"]["altitude"] = cruiseAltitude

referenceMission.segment["descent"]

referenceMission.segment["abortClimb"]

referenceMission.segment["abortDescent"]

referenceMission.segment["landing"]["altitude"] = 0

referenceMission.segment["shutdown"]["altitude"] = 0

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
    return (energyRequiredOfBattery / batteryEnergyDensity) * g
        
conventional = Powerplant()
conventional.eta = internalCombustionMotorEfficiency * shaftEfficiency * conventional.propeller.eta
conventional.fuelUsedForEnergyUsed = _conventionalFuelUsed

def _conventionalFuelUsed(missionSegment, energyUsed):
    fuelEnergyUsed = energyUsed / conventional.eta
    return (fuelEnergyUsed / avgasEnergyDensity) * g # in kg

genericPropeller = Propeller()
genericPropeller.eta = 0.8