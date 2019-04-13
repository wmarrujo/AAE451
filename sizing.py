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

def getPerformanceParameters(airplaneName, drivingParameters, cache=True):
    initialAirplane = defineAirplane(airplaneName, drivingParameters)
    finalAirplane = simulateAirplane(initialAirplane)
    pass # return performanceParameters dict

################################################################################
# AIRCRAFT HANDLING
################################################################################

def defineAirplane(airplaneName, drivingParameters, cache=True):
    pass # return an airplane object
    # also, save it to memory

def simulateAirplane(initialAirplane, mission, cache=True):
    """returns the airplane at its final state, or None if the simulation failed"""
    airplane = copy.deepcopy(initialAirplane)
    
    success = mission.simulate(timestep, airplane, simulationRecordingFunction)
    
    if cache:
        # save the simulation
        if success:
            pass # save the final aircraft state
    
    # run simulation, save to global simulation object, return true on success, return final airplane, or none if failure

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