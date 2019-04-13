# PATHS

import sys
import os
hereDirectory = os.path.dirname(os.path.abspath(__file__))
rootDirectory = hereDirectory

simulationPath = os.path.join(rootDirectory, "simulations")
sys.path.append(simulationPath)

# LOCAL DEPENDENCIES

from utilities import *

from parameters import *
from missions import *

# EXTERNAL DEPENDENCIES

import copy
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
    "initial gross weight"]

# PERFORMANCE PARAMETERS

performanceParametersKeys = [
    "empty weight",
    "takeoff feild length",
    "range",
    "average ground speed",
    "flight time"]

# SIMULATION PARAMETERS

simulationParametersKeys = [
    "time",
    "segment",
    "position",
    "altitude",
    "weight",
    "thrust"]

################################################################################
# PERFORMANCE
################################################################################



################################################################################
# AIRCRAFT HANDLING
################################################################################



################################################################################
# CACHING
################################################################################

if not os.path.exists(simulationPath): # simulation path does not exist
    os.makedirs(simulationPath) # create it






################################################################################
# PERFORMANCE
################################################################################

# TODO: only make the caching directory when it finishes & will write.
# TODO: put a note in the directory if the simulation failed (but still put the initial airplane configuration, maybe write that part it in the airplane definition)
# TODO: test each piece, initialAirplane, simulation, finalAirplane separately (maybe simulation & final together?)

def getPerformanceParameters(drivingParameters, defaultAirplane, cache=True):
    # get from cache if the simulation has already been done
    dirName = defaultAirplane.name + "-" + compareValue(compareValue(drivingParameters) + compareValue(defaultAirplane))
    dir = os.path.join(simulationPath, dirName)
    cached = os.path.exists(dir)
    if cache and not cached: # only if you want to cache
        os.makedirs(dir) # make dir so that it can be read from and written to later
    initialObjectFilePath = os.path.join(dir, "initial.pyobj")
    finalObjectFilePath = os.path.join(dir, "final.pyobj")
    simulationFilePath = os.path.join(dir, "simulation.csv")

    print("Getting Aircraft Parameters for {}".format(dirName), end="", flush=True)

    if not cache or not cached: # if it shouldn't cache or was not cached, continue to simulate
        print(" - No Cache, Simulating")

        # DEFINE AIRPLANE

        airplane = defineAirplane(drivingParameters, defaultAirplane)
        initialAirplane = copy.deepcopy(airplane)
        if cache: # only if you want to cache
            saveObject(airplane, initialObjectFilePath) # save initial state

        # RUN SIMULATION

        simulation = {"time":[], "segment":[], "position":[], "altitude":[], "weight":[], "thrust":[]}
        def recordingFunction(time, segmentName, airplane):
            W = AirplaneWeight(airplane)
            T = AirplaneThrust(airplane)

            simulation["time"].append(time)
            simulation["segment"].append(segmentName)
            simulation["position"].append(airplane.position)
            simulation["altitude"].append(airplane.altitude)
            simulation["weight"].append(W)
            simulation["thrust"].append(T)

        success = designMission.simulate(timestep, airplane, recordingFunction)

        finalAirplane = airplane
        if cache: # only if you want to cache
            dictToCSV(simulationFilePath, simulation) # save simulation
            saveObject(airplane, finalObjectFilePath) # save final state

    else: # was cached
        print(" - Cache exists, Loading From Cache")
        initialAirplane = loadObject(initialObjectFilePath)
        finalAirplane = loadObject(finalObjectFilePath)
        simulation = CSVToDict(simulationFilePath)

    # CALCULATE PERFORMANCE
    # initialAirplane, finalAirplane, & simulation are defined by now
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

    return {
        "empty weight": emptyWeight,
        "takeoff distance": dTO,
        "range": range,
        "average ground speed": avgGroundSpeedInCruise,
        "flight time": cruiseFlightTime,
        "fuel used": fuelWeightUsed}

################################################################################
# AIRPLANE
################################################################################

def defineAirplane(drivingParameters, defaultAirplane):
    print("Closing Aircraft Weight")

    WS = drivingParameters[0]
    PW = drivingParameters[1]

    airplane = copy.deepcopy(defaultAirplane)

    # MODIFY AIRPLANE OBJECT TO DRIVING PARAMETERS

    def defineAirplaneWithX(A, X):
        B = copy.deepcopy(A)
        S = B.wing.planformArea
        Engines = B.engines
        W0 = X[0] # initial gross weight
        We = EmptyWeight(A)
        Wpay = PayloadWeight(A)

        S = W0 / WS
        Wf = W0 - We - Wpay
        B.initialGrossWeight = W0
        B.powerplant.fuelMass = Wf/g # put on just enough fuel to get through mission
        B.wing.setPlanformAreaHoldingAspectRatio(S)
        for engine in Engines:
            engine.maxPower = PW/len(Engines) * W0 # TODO: assuming all engines are the same size, change to each proportionally if needed

        return B

    # CLOSE WEIGHT

    def functionToMinimize(X):
        A = defineAirplaneWithX(airplane, X)

        WFe = A.powerplant.emptyFuelMass

        success = designMission.simulate(timestep, A)
        penalty = 0 if success else 1e10 # make sure it actually finishes

        WFf = FuelWeight(A)

        return WFf - WFe + penalty # fuel weight at end of mission should be 0

    X0 = [convert(3500, "lb", "N")] # [W0]
    #CS = [(0, None)] # contraints
    result = root(functionToMinimize, X0)
    XE = result["x"]
    airplane = defineAirplaneWithX(defaultAirplane, XE)

    # RETURN CLOSED AIRPLANE

    return airplane
