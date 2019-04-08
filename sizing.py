from utilities import *
from parameters import *
from missions import *

import copy
from scipy.optimize import root
import sys
import os
simulationPath = os.path.join(sys.path[0], "simulations")
sys.path.append(simulationPath)

################################################################################
# PERFORMANCE
################################################################################

def getPerformanceParameters(drivingParameters, defaultAirplane, cache=True):
    # get from cache if the simulation has already been done
    dirName = defaultAirplane.name + "-" + compareValue(compareValue(drivingParameters) + compareValue(defaultAirplane))
    dir = os.path.join(simulationPath, dirName)
    cached = os.path.isdir(dir)
    if cache and not cached: # only if you want to cache
        os.mkdir(dir) # make dir so that it can be read from and written to later
    initialObjectFilePath = os.path.join(dir, "initial.pyobj")
    finalObjectFilePath = os.path.join(dir, "final.pyobj")
    simulationFilePath = os.path.join(dir, "simulation.csv")
    
    if not cache or not cached: # if it shouldn't cache or was not cached, continue to simulate
        
        # DEFINE AIRPLANE
        
        airplane = defineAirplane(drivingParameters, defaultAirplane)
        initialAirplane = copy.deepcopy(airplane)
        if cache: # only if you want to cache
            saveObject(airplane, initialObjectFilePath) # save initial state
        
        # RUN SIMULATION
        
        simulation = {"time":[], "segment":[]}
        def recordingFunction(time, segmentName, airplane):
            simulation["time"].append(time)
            simulation["segment"].append(segmentName)
            # TODO: fill in with anything else that you want the simulation to record to calculate the performance parameters with or to plot later
        
        success = designMission.simulate(timestep, airplane, recordingFunction)
        
        finalAirplane = airplane
        if cache: # only if you want to cache
            dictToCSV(simulationFilePath, simulation) # save simulation
            saveObject(airplane, finalObjectFilePath) # save final state
        
    else: # was cached
        initialAirplane = loadObject(initialObjectFilePath)
        finalAirplane = loadObject(finalObjectFilePath)
        simulation = CSVToDict(simulationFilePath)
    
    # CALCULATE PERFORMANCE
    # initialAirplane, finalAirplane, & simulation are defined by now
    
    
    
    return {}

################################################################################
# AIRPLANE
################################################################################

def defineAirplane(drivingParameters, defaultAirplane):
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
        B.wing.setPlanformAreaWhileMaintainingAspectRatio(S)
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