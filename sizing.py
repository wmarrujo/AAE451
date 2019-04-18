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
    "thrust",
    "speed",
    "center of gravity"]

# PERFORMANCE PARAMETERS

performanceParametersKeys = [
    "empty weight",
    "takeoff field length",
    "range",
    "average ground speed",
    "flight time",
    "fuel used"]

################################################################################
# SIMULATION LIFECYCLE
################################################################################

simulation = {} # define as global to write to during simulation

def initializeSimulation():
    global simulation
    simulation = dict(zip(simulationParametersKeys, [[] for n in range(len(simulationParametersKeys))])) # put in headers as keys

def simulationRecordingFunction(time, segmentName, airplane):
    global simulation
    W = AirplaneWeight(airplane)
    T = AirplaneThrust(airplane)
    V = airplane.speed
    CG = CenterOfGravity(airplane)
    
    simulation["time"].append(time)
    simulation["segment"].append(segmentName)
    simulation["position"].append(airplane.position)
    simulation["altitude"].append(airplane.altitude)
    simulation["weight"].append(W)
    simulation["thrust"].append(T)
    simulation["speed"].append(V)
    simulation["center of gravity"].append(CG)

################################################################################
# PERFORMANCE
################################################################################

def getPerformanceParameters(airplaneName, drivingParameters, mission, cache=True, silent=False):
    global simulation
    
    # GET AIRPLANE AND SIMULATION DATA
    
    id = airplaneDefinitionID(airplaneName, drivingParameters)
    print("Getting Performance Parameters for Airplane       - {:10.10}".format(id)) if not silent else None
    initialAirplane = loadInitialAirplane(id, silent=silent) if cache and initialAirplaneCached(id) else defineAirplane(airplaneName, drivingParameters, mission, silent=silent)
    if cache and simulationCached(id):
        simulation = loadSimulation(id, silent=silent)
        finalAirplane = loadFinalAirplane(id, silent=silent) if finalAirplaneCached(id) else None
    else:
        finalAirplane = simulateAirplane(initialAirplane, mission, cache=cache, airplaneID=id, silent=silent)
    
    # CALCULATE PERFORMANCE VALUES
    
    ts = simulation["time"]
    ss = simulation["segment"]
    ps = simulation["position"]
    hs = simulation["altitude"]
    Ws = simulation["weight"]
    Ts = simulation["thrust"]
    
    #emptyWeight = EmptyWeight(initialAirplane)
    emptyWeight = initialAirplane.emptyMass*g
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
        "takeoff field length": dTO,
        "range": cruiseRange,
        "average ground speed": avgGroundSpeedInCruise,
        "flight time": cruiseFlightTime,
        "fuel used": fuelWeightUsed}

################################################################################
# AIRCRAFT HANDLING
################################################################################

def defineAirplane(airplaneName, drivingParameters, mission, cache=True, silent=False):
    id = airplaneDefinitionID(airplaneName, drivingParameters)
    print("Defining Airplane                                 - {:10.10}".format(id)) if not silent else None
    defineAirplaneSpecifically = airplaneDefinitionFunction(airplaneName)
    
    def setDefiningParameters(drivingParameters, X):
        definingParameters = drivingParameters
        definingParameters["initial gross weight"] = X[0]
        definingParameters["initial fuel weight"] = X[1]
        
        return definingParameters
    
    def functionToFindRootOf(X):
        W0guess = X[0]
        WFguess = X[1]
        
        # apply bounds
        
        if W0guess < 0 or WFguess < 0:
            return [1e10, 1e10] # pseudo bound
        
        # define airplane
        
        definingParameters = setDefiningParameters(drivingParameters, X)
        
        initialAirplane = defineAirplaneSpecifically(definingParameters)
        finalAirplane = simulateAirplane(initialAirplane, mission, cache=False, silent=silent)
        if finalAirplane is None: # the simulation has failed
            return [1e10, 1e10] # huge penalty for optimizer
        
        # calculate values
        
        W0 = AirplaneWeight(initialAirplane)
        WFf = FuelWeight(finalAirplane)
        WFe = finalAirplane.powerplant.emptyFuelMass
        
        return [W0 - W0guess, WFf - WFe] # the gross weight should match the guess and the mission should use all the fuel
    
    X0 = [convert(3500, "lb", "N"), convert(300, "lb", "N")]
    result = root(functionToFindRootOf, X0, tol=1e-1)
    Xf = result["x"]
    definingParameters = setDefiningParameters(drivingParameters, Xf)
    airplane = defineAirplaneSpecifically(definingParameters)
    
    if cache:
        saveInitialAirplane(airplane, id, silent=silent)
    
    print("Airplane Definition Closed", id) if not silent else None
    return airplane

def simulateAirplane(initialAirplane, mission, cache=True, airplaneID=None, silent=False):
    """returns the airplane at its final state, or None if the simulation failed"""
    airplane = copy.deepcopy(initialAirplane)
    
    initializeSimulation()
    finalAirplane = mission.simulate(timestep, airplane, simulationRecordingFunction, silent=silent)
    
    if cache and airplaneID is not None:
        saveSimulation(airplaneID, silent=silent) # save the simulation
        saveFinalAirplane(finalAirplane, airplaneID, silent=silent) # save the final airplane
    
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

def createAirplaneIDDirectoryIfNotMade(airplaneID):
    airplaneDirectory = os.path.join(simulationDirectory, airplaneID)
    if not os.path.exists(airplaneDirectory):
        os.makedirs(airplaneDirectory)

def initialAirplaneCached(airplaneID):
    """checks if the initial airplane for a certain simulation has been cached"""
    return os.path.exists(os.path.join(simulationDirectory, airplaneID, "initial.pyobj"))

def simulationCached(airplaneID):
    """checks if the simulation of the airplane is cached"""
    return os.path.exists(os.path.join(simulationDirectory, airplaneID, "simulation.csv"))

def finalAirplaneCached(airplaneID):
    """checks if the final airplane configuration has been cached"""
    return os.path.exists(os.path.join(simulationDirectory, airplaneID, "final.pyobj"))

def loadInitialAirplane(airplaneID, silent=False):
    print("Loading Initial Airplane Configuration from Cache - {:10.10}".format(airplaneID)) if not silent else None
    return loadObject(os.path.join(simulationDirectory, airplaneID, "initial.pyobj")) if initialAirplaneCached(airplaneID) else None

def loadSimulation(airplaneID, silent=False):
    print("Loading Simulation from Cache                     - {:10.10}".format(airplaneID)) if not silent else None
    return CSVToDict(os.path.join(simulationDirectory, airplaneID, "simulation.csv")) if simulationCached(airplaneID) else {}

def loadFinalAirplane(airplaneID, silent=False):
    print("Loading Final Airplane Configuration from Cache   - {:10.10}".format(airplaneID))
    return loadObject(os.path.join(simulationDirectory, airplaneID, "final.pyobj")) if finalAirplaneCached(airplaneID) else None

def saveInitialAirplane(airplaneObject, airplaneID, silent=False):
    print("Saving Initial Airplane Configuration to Cache    - {:10.10}".format(airplaneID)) if not silent else None
    createAirplaneIDDirectoryIfNotMade(airplaneID)
    saveObject(airplaneObject, os.path.join(simulationDirectory, airplaneID, "initial.pyobj"))

def saveSimulation(airplaneID, silent=False):
    global simulation
    print("Saving Simulation to Cache                        - {:10.10}".format(airplaneID)) if not silent else None
    createAirplaneIDDirectoryIfNotMade(airplaneID)
    dictToCSV(os.path.join(simulationDirectory, airplaneID, "simulation.csv"), simulation)

def saveFinalAirplane(airplaneObject, airplaneID, silent=False):
    print("Saving Final Airplane Configuration to Cache      - {:10.10}".format(airplaneID)) if not silent else None
    createAirplaneIDDirectoryIfNotMade(airplaneID)
    saveObject(airplaneObject, os.path.join(simulationDirectory, airplaneID, "final.pyobj"))
