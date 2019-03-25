from utilities import *
from stdatmo import *
from convert import convert
from parameters import *
from constants import *

from scipy import *
from scipy.optimize import minimize
import copy

################################################################################
# INFORMATION FUNCTIONS
################################################################################

def AirplaneWeight(airplane): # TODO: calculate with airplane.mass?
    Wpay = PayloadWeight(airplane)
    Wfuel = FuelWeight(airplane)
    Wempty = EmptyWeight(airplane)
    
    return Wpay + Wfuel + Wempty

def PayloadWeight(airplane):
    Wpax = heavyPassengerWeight if airplane.passengers <= 3 else lightPassengerWeight
    Wbag = heavyPassengerBagWeight if airplane.passengers <= 3 else lightPassengerBagWeight
    pax = airplane.passengers
    pilots = airplane.pilots
    
    return (Wpax + Wbag) * pax + pilotWeight * pilots

def FuelWeight(airplane):
    mf = airplane.powerplant.fuelMass
    
    return mf/g

def EmptyWeight(airplane):
    return airplane.emptyWeight # TODO: temporary, replace with component weight buildup later

def AirplaneReynoldsNumber(airplane):
    rho = densityAtAltitude(airplane.altitude)
    V = airplane.speed
    L = airplane.wing.span
    mu = dynamicViscosityAtAltitude(airplane.altitude)
    
    return rho * V * L / mu

def AirplaneDynamicPressure(airplane):
    rho = densityAtAltitude(airplane.altitude)
    V = airplane.speed
    
    return 0.5 * rho * V**2

def AccelerationOnGround(airplane):
    W = AirplaneWeight(airplane)
    T = AirplaneThrust(airplane)
    D = AirplaneDrag(airplane)
    L = AirplaneLift(airplane)
    mu = runwayFrictionCoefficientNoBrakes
    
    F = T - D - mu*(W-L)
    m = W/g
    return F/m

def enginePower(airplane, engine):
    th = airplane.throttle
    maxP = engine.maxPower
    
    return th * maxP

def AllEnginesPower(airplane):
    th = airplane.throttle
    engines = airplane.engines
    maxPs = [engine.maxPower for engine in engines]
    P = sum([th*maxP for maxP in maxPs])
    
    return P

def AirplaneThrust(airplane):
    V = airplane.speed
    V = 20 if V < 20 else V # m/s # FIXME: find actual static thrust value of propeller & use that
    th = airplane.throttle
    engines = airplane.engines
    maxPs = [engine.maxPower for engine in engines]
    Ps = [th*maxP for maxP in maxPs]
    etaps = [engine.propeller.efficiency for engine in engines]
    PAs = [P*etap for (P, etap) in zip(Ps, etaps)]
    Ts = [PA/V for PA in PAs]
    
    return sum(Ts)

def AirplaneDrag(airplane):
    q = AirplaneDynamicPressure(airplane)
    S = WingPlanformArea(airplane)
    CD = DragCoefficient(airplane) 
    
    return q * S * CD

def WingPlanformArea(airplane):
    b = airplane.wing.span
    c = airplane.wing.chord
    
    return b * c

def ParasiteDrag(airplane):
    altitude = airplane.altitude
    rho = densityAtAltitude(altitude)
    V = airplane.speed
    mu = dynamicViscosityAtAltitude(altitude)
    Sref = WingPlanformArea(airplane)
    CD0miscFactor = airplane.miscellaneousParasiteDragFactor
    
    def componentDragContribution(component):
        FFi = component.formFactor
        Qi = component.interferenceFactor
        Cfi = ComponentSkinFrictionCoefficient(airplane, component)
        Sweti = component.wettedArea
        
        return FFi * Qi * Cfi * Sweti / Sref
    
    CD0Prediction = sum([componentDragContribution(component) for component in airplane.components])
    
    return CD0Prediction * (1+CD0miscFactor)

def ComponentSkinFrictionCoefficient(airplane, component):
    rho = densityAtAltitude(airplane.altitude)
    mu = dynamicViscosityAtAltitude(airplane.altitude)
    V = airplane.speed
    L = component.referenceLength
    
    Re = rho * V * L / mu
    Re = 10 if Re == 0 else Re # make sure log10 has a value
    return 0.455 / (log10(Re)**2.58) # TODO: better approximation?

def InducedDrag(airplane):
    CL = LiftCoefficient(airplane)
    AR = airplane.wing.aspectRatio
    e = airplane.oswaldEfficiencyFactor
    
    return CL**2 / (pi * AR * e)

def DragCoefficient(airplane):
    CD0 = ParasiteDrag(airplane)
    CDi = InducedDrag(airplane)
    CDc = airplane.compressibilityDrag
    
    return CD0 + CDi + CDc

def SteadyLevelFlightLiftCoefficient(airplane):
    qinf = AirplaneDynamicPressure(airplane)
    W = AirplaneWeight(airplane)
    S = WingPlanformArea(airplane)
    
    return W / (qinf * S)

def LiftCoefficient(airplane):
    a = airplane.angleOfAttack
    CL = airplane.wing.airfoil.liftCoefficientAtAngleOfAttack(a)
    
    return CL

def AirplaneLift(airplane):
    q = AirplaneDynamicPressure(airplane)
    S = WingPlanformArea(airplane)
    CL = LiftCoefficient(airplane)
    
    return q * S * CL

def ClimbRangeCredit(airplane, tstep):
    rangeRate = ClimbRangeRate(airplane, tstep)
    
    return rangeRate * tstep

def ClimbRangeRate(airplane, tstep):
    climbRate = ClimbAltitudeRate(airplane)
    flightPathAngle = airplane.flightPathAngle
    
    return climbRate / tan(flightPathAngle)

def ClimbAltitudeCredit(airplane, tstep):
    climbRate = ClimbAltitudeRate(airplane)
    
    return climbRate * tstep

def ClimbAltitudeRate(airplane):
    excessPower = MaxExcessPower(airplane)
    W = AirplaneWeight(airplane)
    
    return excessPower / W

from matplotlib.pyplot import * # DEBUG: just to see, remove later

def MaxExcessPower(airplane):
    Vguess = airplane.speed
    
    def functionToMinimize(V):
        A = copy.deepcopy(airplane) # make sure we're not messing stuff up
        A.speed = V[0] # allow the sub-calculations to use the speed passed in
        
        return -(powerAvailableAtAltitude(A) - PowerRequiredAtAltitude(A))
    
    result = minimize(functionToMinimize, [Vguess], bounds=[(0, None)])
    maxExcessPower = -functionToMinimize(result["x"])
    
    return maxExcessPower

def powerAvailableAtAltitude(airplane):
    T = AirplaneThrust(airplane)
    V = airplane.speed
    
    return T*V

def PowerRequiredAtAltitude(airplane):
    PRSL = PowerRequiredAtSeaLevel(airplane)
    rhoSL = densityAtAltitude(0)
    rhoAlt = densityAtAltitude(airplane.altitude)
    
    return PRSL * (rhoAlt / rhoSL)

def PowerRequiredAtSeaLevel(airplane):
    TRSL = ThrustRequiredAtSeaLevel(airplane)
    V = airplane.speed
    
    return TRSL * V

def ThrustRequiredAtSeaLevel(airplane):
    LoD = CurrentLiftOverDrag(airplane)
    W = AirplaneWeight(airplane)
    
    return W / LoD
    
def CurrentLiftOverDrag(airplane):
    CL = SteadyLevelFlightLiftCoefficient(airplane)
    CD = DragCoefficient(airplane)
    
    return CL/CD
    
def ClimbVelocity(airplane):
    flightPathAngle = airplane.flightPathAngle
    climbRate = ClimbAltitudeRate(airplane)
    
    return climbRate / sin(flightPathAngle)

def TakeoffSpeed(airplane):
    Vstall = StallSpeed(airplane)
    
    return 1.2*Vstall

def StallSpeed(airplane):
    W = AirplaneWeight(airplane)
    rho = densityAtAltitude(airplane.altitude)
    S = airplane.wing.planformArea
    CLmax = airplane.wing.maximumLiftCoefficient
    
    return sqrt(2*W / (rho * S * CLmax))

################################################################################
# UPDATING FUNCTIONS
################################################################################

def UpdateFuel(airplane, tstep):
    P = AllEnginesPower(airplane)
    E = P*tstep
    gas = airplane.powerplant.gas
    battery = airplane.powerplant.battery
    mg = gas.mass if gas is not None else 0
    mb = battery.mass if battery is not None else 0
    generator = airplane.powerplant.generator
    percentElectric = airplane.powerplant.percentElectric
    generatorOn = airplane.powerplant.generatorOn
    
    Eb = E*percentElectric # energy requested of battery
    Eg = E*(1-percentElectric) + (generator.power*tstep*generator.efficiency if generatorOn else 0) # energy requested of gas
    
    if battery is not None:
        battery.energy -= Eb
    if gas is not None:
        gas.mass -= Eg/gas.energyDensity

################################################################################
# COST FUNCTIONS
################################################################################

# This is based on the DAPCA IV model in Raymer v6 Ch. 18.4.2
# DAPCA assumes all aluminum framing, but provides fudge factors to adjust hour calculations

def engineeringHours(airplane):
    We = airplane.emptyWeight / g # DAPCA model needs empty weight in [kgs]
    V = None  # Maximum velocity [km/h]
    Q = Aiplane.productionQuantityNeeded
    
    return 5.18 * (We**0.777) * (V**0.894) * (Q**0.163)

def toolingHours(airplane):
    We = airplane.emptyWeight / g # DAPCA model needs empty weight in [kgs]
    V = None  # Maximum velocity [km/h]
    Q = Aiplane.productionQuantityNeeded
    
    return 7.22 * (We**0.777) * (V**0.696) * (Q**0.263)

def manufacturingHours(airplane):
    We = airplane.emptyWeight / g # DAPCA model needs empty weight in [kgs]
    V = None  # Maximum velocity [km/h]
    Q = Aiplane.productionQuantityNeeded
    
    return 10.5 * (We**0.82) * (V**0.484) * (Q**0.641)

def qualityControlHours(airplane):
    mfgHours = manufacturingHours(airplane)
    
    return 0.133 * mfgHours

def developmentSupportCost(airplane):
    We = airplane.emptyWeight / g # DAPCA model needs empty weight in [kgs]
    V = None  # Maximum velocity [km/h]
    iR = inflation2012to2019
    
    return iR * 67.4 * (We**0.630) * (V**1.3)

def flightTestCost(airplane):
    We = airplane.emptyWeight / g # DAPCA model needs empty weight in [kgs]
    V = None  # Maximum velocity [km/h]
    FTA = airplane.numberFlightTestAircraft
    iR = inflation2012to2019
    
    return iR * 1947 * (We**0.325) * (V**0.822) * (FTA**1.21)

def manufacturingMaterialsCost(airplane):
    We = airplane.emptyWeight / g # DAPCA model needs empty weight in [kgs]
    V = None  # Maximum velocity [km/h]
    Q = Aiplane.productionQuantityNeeded
    iR = inflation2012to2019
    
    return iR * 31.2 * (We**0.921) * (V**0.621) * (Q**0.799)

def passengerAdditionalCost(airplane):
    N = airplane.passengers
    P = airplane.pilot
    Cp = generalAviationPassengerCostFactor
    iR = inflation2012to2019
    
    return Cp * iR * (N + P)
