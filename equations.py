from utilities import *
from stdatmo import *
from convert import convert
from parameters import *
from constants import *

################################################################################
# INFORMATION FUNCTIONS
################################################################################

def PayloadWeight(Mission):
    Wpax = heavyPassengerWeight if Mission.passengers <= 3 else lightPassengerWeight
    Wbag = heavyPassengerBagWeight if Mission.passengers <= 3 else lightPassengerBagWeight
    pax = Mission.passengers
    pilots = Mission.pilots

    return (Wpax + Wbag) * pax + pilotWeight * pilots

def AirplaneReynoldsNumber(Airplane):
    rho = densityAtAltitude(Airplane.altitude)
    V = Airplane.speed
    L = Airplane.wing.span
    mu = dynamicViscosityAtAltitude(Airplane.altitude)

################################################################################
# UPDATING FUNCTIONS
################################################################################

def runEngine(Airplane, tstep):
    th = Airplane.throttle
    engines = Airplane.engines
    maxPs = [engine.maxPower for engine in engines]
    P = sum([th*maxP for maxP in maxPs])