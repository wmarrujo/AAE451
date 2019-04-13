# PATHS

import sys
import os
hereDirectory = os.path.dirname(os.path.abspath(__file__))
rootDirectory = hereDirectory

simulationDirectory = os.path.join(rootDirectory, "simulations")
sys.path.append(simulationDirectory)
configurationsDirectory = os.path.join(rootDirectory, "configurations")
sys.path.append(configurationsDirectory)

# LOCAL DEPENDENCIES

from utilities import *

from parameters import *
from missions import *

# EXTERNAL DEPENDENCIES

import copy
from importlib import import_module
from scipy.optimize import root

################################################################################
# DEBUG: organization

# DEFINE AIRCRAFT
# CLOSE AIRCRAFT
# SIMULATE AIRCRAFT
# CALCULATE PERFORMANCE PARAMETERS
# CACHE AIRCRAFT
# CACHE AIRCRAFT SIMULATION
# LOAD AIRCRAFT FROM CACHE
# LOAD AIRCRAFT SIMULATION FROM CACHE

# DRIVING PARAMETERS
# DEFINING PARAMETERS
# PERFORMANCE PARAMETERS
# SIMULATION PARAMETERS

################################################################################
# PARAMETERS
################################################################################

# DRIVING PARAMETERS

drivingParametersKeys = [
    "wing loading",
    "power to weight ratio"]

# DEFINING PARAMETERS

definingParametersKeys = drivingParametersKeys + [
    "initial gross weight",
    "initial fuel weight"]

# SIMULATION PARAMETERS

simulationParametersKeys = [
    "time",
    "segment",
    "position",
    "altitude",
    "weight",
    "thrust"]

# PERFORMANCE PARAMETERS

performanceParametersKeys = [
    "empty weight",
    "takeoff feild length",
    "range",
    "average ground speed",
    "flight time",
    "fuel used"]

################################################################################
# SIMULATION LIFECYCLE
################################################################################

simulation = {} # define as global to write to during simulation

def initializeSimulation():
    simulation = dict(zip(simulationParametersKeys, [[]]*len(simulationParametersKeys))) # put in headers as keys

def simulationRecordingFunction(time, segmentName, airplane):
    W = AirplaneWeight(airplane)
    T = AirplaneThrust(airplane)
    
    simulation["time"].append(time)
    simulation["segment"].append(segmentName)
    simulation["position"].append(airplane.position)
    simulation["altitude"].append(airplane.altitude)
    simulation["weight"].append(W)
    simulation["thrust"].append(T)

################################################################################
# PERFORMANCE
################################################################################

def getPerformanceParameters(airplaneName, drivingParameters, mission, cache=True):
    
    # GET AIRPLANE AND SIMULATION DATA
    
    id = airplaneDefinitionID(airplaneName, drivingParameters)
    initialAirplane = loadInitialAirplane(id) if cache and initialAirplaneCached(id) else defineAirplane(airplaneName, drivingParameters, mission)
    if cache and simulationCached(id):
        simulation = loadSimulation(id)
        finalAirplane = loadFinalAirplane(id) if finalAirplaneCached(id) else None
    else:
        finalAirplane = simulateAirplane(initialAirplane, mission, cache=cache, airplaneID=id)
    
    # CALCULATE PERFORMANCE VALUES
    
    ts = simulation["time"]
    ss = simulation["segment"]
    ps = simulation["position"]
    hs = simulation["altitude"]
    Ws = simulation["weight"]
    Ts = simulation["thrust"]
    
    emptyWeight = EmptyWeight(initialAirplane)
    dTO = ps[firstIndex(hs, lambda h: h >= 50)]
    range = ps[-1]
    cruiseStartIndex = firstIndex(ss, lambda s: s == "cruise")
    cruiseEndIndex = lastIndex(ss, lambda s: s == "cruise")
    cruiseFlightTime = ts[cruiseEndIndex] - ts[cruiseStartIndex]
    cruiseRange = ps[cruiseEndIndex] - ps[cruiseStartIndex]
    avgGroundSpeedInCruise = cruiseRange / cruiseFlightTime # TODO: are we sure we want this just for cruise? or do we need to count the startup & stuff too
    fuelWeightUsed = Ws[0] - Ws[-1]
    
    # RETURN PERFORMANCE PARAMETERS DICTIONARY
    
    return {
        "empty weight": emptyWeight,
        "takeoff distance": dTO,
        "range": range,
        "average ground speed": avgGroundSpeedInCruise,
        "flight time": cruiseFlightTime,
        "fuel used": fuelWeightUsed}

################################################################################
# AIRCRAFT HANDLING
################################################################################

def defineAirplane(airplaneName, drivingParameters, mission, cache=True):
    id = airplaneDefinitionID(airplaneName, drivingParameters)
    defineAirplaneSpecifically = airplaneDefinitionFunction(airplaneName)
    
    def functionToFindRootOf(X):
        definingParameters = drivingParameters
        definingParameters["initial gross weight"] = X[0]
        definingParameters["initial fuel weight"] = X[1]
        
        initialAirplane = defineAirplaneSpecifically(definingParameters)
        finalAirplane = simulateAirplane(initialAirplane, mission, cache=False)
        if finalAirplane is None: # the simulation has failed
            return 1e10 # huge penalty for optimizer
        
        WF0 = FuelWeight(initialAirplane)
        WFf = FuelWeight(finalAirplane)
        
        # FIXME: might have to change this to a minimizer since there are now 2 variables
        return WFf - WFi # there should be no fuel at the end of the mission
    
    X0 = [convert(3500, "lb", "N"), convert(300, "lb", "N")]
    result = root(functionToFindRootOf, X0)
    Xf = result["x"]
    airplane = defineAirplaneSpecifically(definingParameters)
    
    if cache:
        saveInitialAirplane(airplane, id)
    
    return airplane

def simulateAirplane(initialAirplane, mission, cache=True, airplaneID=None):
    """returns the airplane at its final state, or None if the simulation failed"""
    airplane = copy.deepcopy(initialAirplane)
    
    finalAirplane = mission.simulate(timestep, airplane, simulationRecordingFunction)
    
    if cache and airplaneID is not None:
        saveSimulation(airplaneID) # save the simulation
        saveFinalAirplane(finalAirplane, airplaneID) # save the final airplane
    
    return finalAirplane

################################################################################
# FILE HANDLING
################################################################################

if not os.path.exists(simulationDirectory): # simulation path does not exist
    os.makedirs(simulationDirectory) # create it

def airplaneDefinitionID(airplaneName, drivingParameters):
    return compareValue(airplaneName, drivingParameters)

def airplaneDefinitionFunction(airplaneName):
    module = import_module(airplaneName)
    return module.defineAirplane

def initialAirplaneCached(airplaneID):
    """checks if the initial airplane for a certain simulation has been cached"""
    pass

def simulationCached(airplaneID):
    """checks if the simulation of the airplane is cached"""
    pass

def finalAirplaneCached(airplaneID):
    """checks if the final airplane configuration has been cached"""
    pass

def loadInitialAirplane(airplaneID):
    pass

def loadSimulation(airplaneID):
    pass

def loadFinalAirplane(airplaneID):
    pass

def saveInitialAirplane(airplaneObject, airplaneID):
    pass

def saveSimulation(airplaneID):
    pass

def saveFinalAirplane(airplaneObject, airplaneID):
    pass