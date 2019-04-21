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
from scipy.spatial.distance import euclidean as norm
from pathlib import Path

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
    "cg",
    "gas mass"]

# PERFORMANCE PARAMETERS

performanceParametersKeys = [
    "empty weight",
    "takeoff field length",
    "landing field length",
    "range",
    "average ground speed",
    "flight time",
    "fuel used"]

################################################################################
# AIRPLANE CREATION
################################################################################

def closeAircraftDesign(airplaneDefinitionFunction, drivingParameters, designMission, silent=False):
    # DEPENDENCIES
    
    def setDefiningParameters(drivingParameters, X):
        definingParameters = drivingParameters
        definingParameters["initial gross weight"] = X[0]
        definingParameters["initial fuel weight"] = X[1]
        
        return definingParameters
    
    def functionToFindRootOf(X):
        # define airplane
        definingParameters = setDefiningParameters(drivingParameters, X)
        initialAirplane = airplaneDefinitionFunction(definingParameters)
        # simulate airplane
        simulationResults = simulateAirplane(initialAirplane, designMission, silent=False)
        initialAirplane = simulationResults["initial airplane"]
        simulation = simulationResults["simulation"]
        finalAirplane = simulationResults["final airplane"]
        succeeded = simulationResults["succeeded"]
        
        # calculate resultant point
        if succeeded:
            guessedGrossWeight = definingParameters["initial gross weight"]
            predictedGrossWeight = AirplaneWeight(initialAirplane)
            grossWeightDifference = abs(guessedGrossWeight - predictedGrossWeight)
            emptyFuelMass = finalAirplane.powerplant.emptyFuelMass
            finalFuelMass = finalAirplane.powerplant.fuelMass
            
            result = [grossWeightDifference, finalFuelMass - emptyFuelMass]
        else:
            result = [1e10, 1e10] # pseudo bound
        
        print(X, "->", result)
        return result
    
    # INITIALIZATION
    
    tolerance = 1e-1
    guess = [convert(3000, "lb", "N"), convert(300, "lb", "N")]
    
    # MINIMIZATION
    
    result = root(functionToFindRootOf, guess, tol=tolerance)
    closestGuess = result["x"]
    airplane = airplaneDefinitionFunction(setDefiningParameters(drivingParameters, closestGuess))
    closed = norm([0, 0], result["fun"]) <= tolerance*10
    
    return {
        "airplane": airplane,
        "closed": closed}

################################################################################
# SIMULATION
################################################################################

def simulateAirplane(initialAirplane, mission, silent=False):
    # INITIALIZATION
    
    succeeded = True
    airplane = copy.deepcopy(initialAirplane)
    simulation = dict(zip(simulationParametersKeys, [[] for n in range(len(simulationParametersKeys))])) # put in headers as keys
    
    def simulationRecordingFunction(time, segmentName, airplane):
        W = AirplaneWeight(airplane)
        T = AirplaneThrust(airplane)
        V = airplane.speed
        cg = CenterGravity(airplane)
        mg = airplane.powerplant.gas.mass if airplane.powerplant.gas else 0
        
        simulation["time"].append(time)
        simulation["segment"].append(segmentName)
        simulation["position"].append(airplane.position)
        simulation["altitude"].append(airplane.altitude)
        simulation["weight"].append(W)
        simulation["thrust"].append(T)
        simulation["speed"].append(V)
        simulation["cg"].append(cg)
        simulation["gas mass"].append(mg)
    
    # SIMULATION
    
    finalAirplane = mission.simulate(timestep, airplane, simulationRecordingFunction, silent=silent)
    
    # RETURN ALL DATA
    
    return {
        "initial airplane": initialAirplane,
        "final airplane": finalAirplane,
        "simulation": simulation,
        "succeeded": succeeded}

################################################################################
# PERFORMANCE
################################################################################

def getPerformanceParameters(initialAirplane, simulation, finalAirplane):
    # GET DATA FROM SIMULATION
    
    ts = simulation["time"]
    ss = simulation["segment"]
    ps = simulation["position"]
    hs = simulation["altitude"]
    
    # CALCULATE PERFORMANCE PARAMETERS
    
    emptyWeight = initialAirplane.emptyMass*g
    dTO = ps[firstIndex(hs, lambda h: obstacleHeight <= h)]
    dL = ps[-1] - ps[lastIndex(hs, lambda h: obstacleHeight <= h)]
    range = ps[-1]
    missionTime = ts[-1]
    
    # RETURN PERFORMANCE PARAMETERS DICTIONARY
    
    return {
        "empty weight": emptyWeight,
        "takeoff field length": dTO,
        "landing field length": dL,
        "range": range,
        "mission time": missionTime}








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

    X0 = [convert(2711, "lb", "N"), convert(300, "lb", "N")]
    result = root(functionToFindRootOf, X0, tol=1e-1)
    Xf = result["x"]
    Xr = result["fun"]
    
    tolerance = 30 # within "30" of the 0 point = "close enough"
    if tolerance < norm([0, 0], Xr): # if it didn't actually converge
        print("Aircraft did not close ({})".format(norm([0, 0], Xf))) if not silent else None
        saveNotConvergedMarker(id)
    
    definingParameters = setDefiningParameters(drivingParameters, Xf)
    airplane = defineAirplaneSpecifically(definingParameters)
    
    if cache:
        saveInitialAirplane(airplane, id, silent=silent)
    
    print("Airplane Definition Finished                      - {:10.10}".format(id)) if not silent else None
    return airplane

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

def isNotConverged(airplaneID):
    return os.path.exists(os.path.join(simulationDirectory, airplaneID, "notconverged"))

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

def saveNotConvergedMarker(airplaneID):
    createAirplaneIDDirectoryIfNotMade(airplaneID)
    Path(os.path.join(simulationDirectory, airplaneID, "notconverged")).touch()
