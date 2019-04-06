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
        print("X:", X)
        A = defineAirplaneWithX(airplane, X)
        
        success = designMission.simulate(timestep, A)
        penalty = 0 if success else 1e10 # make sure it actually finishes
        
        WFf = FuelWeight(A)
        
        print(WFf, penalty)
        return abs(WFf) + penalty # fuel weight at end of mission should be 0
    
    X0 = [convert(3500, "lb", "N")] # [W0]
    CS = [(0, None)] # contraints
    result = minimize(functionToMinimize, X0, bounds=CS)
    XE = result["x"]
    airplane = defineAirplaneWithX(defaultAirplane, XE)
    
    # RETURN CLOSED AIRPLANE
    
    return airplane