from utilities import *
from parameters import *
from missions import *

import copy
from scipy.optimize import minimize

################################################################################
# PERFORMANCE
################################################################################

def getPerformanceParameters(drivingParameters, defaultAirplane):
    # DEFINE AIRPLANE
    
    airplane = defineAirplane(drivingParameters, defaultAirplane)
    
    # RUN SIMULATION
    
    
    
    # CALCULATE PERFORMANCE
    
    
    
    # TODO: define airplane
    # TODO: run a simulation with that airplane
    # TODO: calculate the performance parameters with that airplane & simulation

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
        S = airplane.wing.planformArea
        Engines = airplane.engines
        W0 = X[0] # initial gross weight
        
        S = W0 / WS
        B.InitialGrossWeight = W0
        B.wing.setPlanformAreaWhileMaintainingAspectRatio(S)
        for engine in Engines:
            engine.maxPower = PW/len(Engines) * B.InitialGrossWeight # TODO: assuming all engines are the same size, change to each proportionally if needed
        
        return B
    
    # CLOSE WEIGHT
    
    def functionToMinimize(X):
        A = defineAirplaneWithX(airplane, X)
        
        success = designMission.simulate(timestep, A)
        penalty = 0 if success else float("inf") # make sure it actually finishes
        
        FW = FuelWeight(A) # fuel weight at end of mission
        
        print("FW:", FW, penalty)
        return abs(FW) + penalty # fuel weight at end of mission should be 0
    
    X0 = [convert(4000, "lb", "N")] # [W0]
    CS = [(0, None)] # contraints
    result = minimize(functionToMinimize, X0, bounds=CS)
    XE = result["x"]
    airplane = defineAirplaneWithX(defaultAirplane, XE)
    
    # RETURN CLOSED AIRPLANE
    
    return airplane