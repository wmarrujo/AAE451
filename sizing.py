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
# LIFECYCLE
################################################################################

def getAirplaneDesignData(airplaneName, drivingParameters, designMission, silent=False):
    id = airplaneDefinitionID(airplaneName, drivingParameters)
    
    # get initial airplane
    initialDesignAirplane = loadAirplaneConfiguration(id, "design-initial")
    if initialDesignAirplane is None: # not cached
        print("Creating Design Configuration                                    - {:10.10}".format(id)) if not silent else None
        # define airplane
        defineSpecificAirplane = airplaneDefinitionFunction(airplaneName)
        closureResult = closeAircraftDesign(defineSpecificAirplane, drivingParameters, designMission, silent=silent)
        initialDesignAirplane = closureResult["airplane"]
        closed = closureResult["closed"]
        # cache results
        saveAirplaneConfiguration(initialDesignAirplane, id, "design-initial")
        print("Design Aircraft " + ("CLOSED" if closed else "DID NOT CLOSE")) if not silent else None
    else:
        print("Loaded Design Initial Configuration                              - {:10.10}".format(id)) if not silent else None
    
    # get simulation results
    designSimulation = loadSimulation(id, "design-simulation")
    finalDesignAirplane = loadAirplaneConfiguration(id, "design-final")
    if designSimulation is None: # not cached
        print("Simulating Design Mission                                        - {:10.10}".format(id)) if not silent else None
        # simulate
        simulationResult = simulateAirplane(initialDesignAirplane, designMission, silent=silent)
        designSimulation = simulationResult["simulation"]
        finalDesignAirplane = simulationResult["final airplane"]
        succeeded = simulationResult["succeeded"]
        # cache results
        saveSimulation(designSimulation, id, "design-simulation")
        saveAirplaneConfiguration(finalDesignAirplane, id, "design-final")
        print("Design Mission " + ("SUCCEEDED" if succeeded else "DID NOT SUCCEED")) if not silent else None
    else: # cached
        print("Loaded Design Configuration Design Mission Simulation            - {:10.10}".format(id)) if not silent else None
        print("Loaded Design Final Configuration                                - {:10.10}".format(id)) if not silent else None
    
    return {
        "initial airplane": initialDesignAirplane,
        "simulation": designSimulation,
        "final airplane": finalDesignAirplane}

def getReferenceMissionData(airplaneName, drivingParameters, designMission, referenceMission, referenceMissionName="reference", silent=False):
    id = airplaneDefinitionID(airplaneName, drivingParameters)
    
    # get initial airplane
    initialReferenceAirplane = loadAirplaneConfiguration(id, referenceMissionName + "-initial")
    if initialReferenceAirplane is None: # not cached
        # load the design airplane
        initialDesignAirplane = loadAirplaneConfiguration(id, "design-initial")
        if initialDesignAirplane is None: # not cached
            print("Creating Design Configuration                                    - {:10.10}".format(id)) if not silent else None
            # define airplane
            defineSpecificAirplane = airplaneDefinitionFunction(airplaneName)
            closureResult = closeAircraftDesign(defineSpecificAirplane, drivingParameters, designMission, silent=silent)
            initialDesignAirplane = closureResult["airplane"]
            closed = closureResult["closed"]
            # cache results
            saveAirplaneConfiguration(initialDesignAirplane, id, "design-initial")
            print("Design Aircraft " + ("CLOSED" if closed else "DID NOT CLOSE")) if not silent else None
        else:
            print("Loaded Design Initial Configuration                              - {:10.10}".format(id)) if not silent else None
        # close reference version of design airplane
        print("Creating Reference Configuration                                 - {:10.10}".format(id)) if not silent else None
        closureResult = closeFuelOnly(initialDesignAirplane, referenceMission, silent=silent)
        initialReferenceAirplane = closureResult["airplane"]
        closed = closureResult["closed"]
        # cache results
        saveAirplaneConfiguration(initialReferenceAirplane, id, referenceMissionName + "-initial")
        print("Reference Aircraft " + ("CLOSED" if closed else "DID NOT CLOSE")) if not silent else None
    else:
        print("Loaded Reference Initial Configuration                           - {:10.10}".format(id)) if not silent else None
    
    # get simulation results
    referenceSimulation = loadSimulation(id, referenceMissionName + "-simulation")
    finalReferenceAirplane = loadAirplaneConfiguration(id, referenceMissionName + "-final")
    if referenceSimulation is None: # not cached
        print("Simulating Reference Mission                                     - {:10.10}".format(id)) if not silent else None
        # simulate
        simulationResult = simulateAirplane(initialReferenceAirplane, referenceMission, silent=silent)
        referenceSimulation = simulationResult["simulation"]
        finalReferenceAirplane = simulationResult["final airplane"]
        succeeded = simulationResult["succeeded"]
        # cache results
        saveSimulation(referenceSimulation, id, referenceMissionName + "-simulation")
        saveAirplaneConfiguration(finalReferenceAirplane, id, referenceMissionName + "-final")
        print("Design Mission " + ("SUCCEEDED" if succeeded else "DID NOT SUCCEED")) if not silent else None
    else: # cached
        print("Loaded Design Configuration Design Mission Simulation            - {:10.10}".format(id)) if not silent else None
        print("Loaded Design Final Configuration                                - {:10.10}".format(id)) if not silent else None
    
    return {
        "initial airplane": initialReferenceAirplane,
        "simulation": referenceSimulation,
        "final airplane": finalReferenceAirplane}

################################################################################
# AIRPLANE CREATION
################################################################################

def closeAircraftDesign(defineSpecificAirplane, drivingParameters, designMission, silent=False):
    # DEPENDENCIES
    
    def setDefiningParameters(drivingParameters, X):
        definingParameters = drivingParameters
        definingParameters["initial gross weight"] = X[0]
        definingParameters["initial fuel weight"] = X[1]
        
        return definingParameters
    
    def functionToFindRootOf(X):
        # define airplane
        definingParameters = setDefiningParameters(drivingParameters, X)
        initialAirplane = defineSpecificAirplane(definingParameters)
        # simulate airplane
        simulationResult = simulateAirplane(initialAirplane, designMission, silent=silent)
        initialAirplane = simulationResult["initial airplane"]
        simulation = simulationResult["simulation"]
        finalAirplane = simulationResult["final airplane"]
        succeeded = simulationResult["succeeded"]
        
        # calculate resultant point
        if succeeded:
            guessedGrossWeight = definingParameters["initial gross weight"]
            predictedGrossWeight = AirplaneWeight(initialAirplane)
            grossWeightDifference = abs(guessedGrossWeight - predictedGrossWeight)
            emptyFuelMass = finalAirplane.powerplant.emptyFuelMass
            finalFuelMass = finalAirplane.powerplant.fuelMass
            
            result = [grossWeightDifference, finalFuelMass*g - emptyFuelMass*g]
        else:
            result = [1e10, 1e10] # pseudo bound
        
        print(X, "->", result, "=>", norm([0, 0], result)) if not silent else None # show convergence
        return result
    
    # INITIALIZATION
    
    guess = [convert(3000, "lb", "N"), convert(300, "lb", "N")]
    
    # ROOT FINDING
    
    result = root(functionToFindRootOf, guess, tol=1e-4)
    closestGuess = result["x"]
    airplane = defineSpecificAirplane(setDefiningParameters(drivingParameters, closestGuess))
    closed = norm([0, 0], result["fun"]) <= sqrt(2) # within 1 N
    
    return {
        "airplane": airplane,
        "closed": closed}

def closeFuelOnly(baseConfiguration, referenceMission, silent=False):
    # DEPENDENCIES
    
    def setInitialAirplaneConfiguration(airplane, X):
        WFguess = X[0]
        A = copy.deepcopy(airplane)
        
        A.powerplant.gas.mass = WFguess / g
        
        return A
    
    def functionToFindRootOf(X):
        # define airplane
        initialAirplane = setInitialAirplaneConfiguration(baseConfiguration, X)
        # simulation
        simulationResult = simulateAirplane(initialAirplane, referenceMission, silent=silent)
        initialAirplane = simulationResult["initial airplane"]
        simulation = simulationResult["simulation"]
        finalAirplane = simulationResult["final airplane"]
        succeeded = simulationResult["succeeded"]
        # post-validation
        if succeeded:
            Wgs = [mg*g for mg in simulation["gas mass"]]
            
            result = [Wgs[0] - Wgs[-1]]
        else:
            result = [1e10] # pseudo bound
        
        print(X, "->", result, "=>", result[0])
        return result
    
    # INITIALIZATION
    
    tolerance = 1e-1
    guess = [convert(300,"lb","N")]
    
    # ROOT FINDING
    result = root(functionToFindRootOf, guess)
    closestGuess = result["x"]
    initialAirplane = setInitialAirplaneConfiguration(baseConfiguration, closestGuess)
    closed = closestGuess <= tolerance # use norm if more than 1 dimension
    
    return {
        "airplane": initialAirplane,
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
# FILE HANDLING
################################################################################

# DIRECTORY HANDLING

if not os.path.exists(simulationDirectory): # simulation path does not exist
    os.makedirs(simulationDirectory) # create it

def createAirplaneIDDirectoryIfNotMade(airplaneID):
    airplaneDirectory = os.path.join(simulationDirectory, airplaneID)
    if not os.path.exists(airplaneDirectory):
        os.makedirs(airplaneDirectory)

def airplaneDefinitionID(airplaneName, drivingParameters):
    return compareValue(airplaneName, drivingParameters)

# CACHING

def loadSimulation(airplaneID, simulationName):
    """returns a cached simulation, or None if it didn't find one"""
    simulationFilePath = os.path.join(simulationDirectory, airplaneID, simulationName + ".csv")
    return CSVToDict(simulationFilePath) if os.path.exists(simulationFilePath) else None

def loadAirplaneConfiguration(airplaneID, configurationName):
    """returns a cached airplane in a certain configuration, or None if it didn't find one"""
    airplaneConfigurationFilePath = os.path.join(simulationDirectory, airplaneID, configurationName + ".pyobj")
    return loadObject(airplaneConfigurationFilePath) if os.path.exists(airplaneConfigurationFilePath) else None

def saveSimulation(simulation, airplaneID, simulationName):
    """saves a simulation"""
    createAirplaneIDDirectoryIfNotMade(airplaneID)
    simulationFilePath = os.path.join(simulationDirectory, airplaneID, simulationName + ".csv")
    dictToCSV(simulationFilePath, simulation)

def saveAirplaneConfiguration(airplaneConfiguration, airplaneID, configurationName):
    createAirplaneIDDirectoryIfNotMade(airplaneID)
    airplaneConfigurationFilePath = os.path.join(simulationDirectory, airplaneID, configurationName + ".pyobj")
    saveObject(airplaneConfiguration, airplaneConfigurationFilePath)

# RESOURCES
    
def airplaneDefinitionFunction(airplaneName):
    module = import_module(airplaneName)
    return module.defineAirplane
