from utilities import *
from stdatmo import *
from convert import convert
from parameters import *
from constants import *

from scipy import *
import copy

################################################################################
# INFORMATION FUNCTIONS
################################################################################

def AirplaneWeight(Airplane): # TODO: calculate with Airplane.mass?
    Wpay = PayloadWeight(Airplane)
    Wfuel = FuelWeight(Airplane)
    Wempty = EmptyWeight(Airplane)

    return Wpay + Wfuel + Wempty

def PayloadWeight(Airplane):
    Wpax = heavyPassengerWeight if Airplane.passengers <= 3 else lightPassengerWeight
    Wbag = heavyPassengerBagWeight if Airplane.passengers <= 3 else lightPassengerBagWeight
    pax = Airplane.passengers
    pilots = Airplane.pilots

    return (Wpax + Wbag) * pax + pilotWeight * pilots

def FuelWeight(Airplane):
    mf = Airplane.powerplant.fuelMass

    return mf/g

def EmptyWeight(Airplane):
    Airplane.emptyWeight # TODO: temporary, replace with component weight buildup later

def AirplaneReynoldsNumber(Airplane):
    rho = densityAtAltitude(Airplane.altitude)
    V = Airplane.speed
    L = Airplane.wing.span
    mu = dynamicViscosityAtAltitude(Airplane.altitude)

    return rho * V * L / mu

def AirplaneDynamicPressure(Airplane):
    rho = densityAtAltitude(Airplane.altitude)
    V = Airplane.speed

    return 0.5 * rho * V**2

def accelerationOnGroundTakeoff(Airplane):
    W = AirplaneWeight(Airplane)
    T = AirplaneThrust(Airplane)
    D = TakeoffAirplaneDrag(Airplane)
    L = TakoffAirplaneLift(Airplane)
    mu = runwayFrictionCoefficientNoBrakes

    return g/W * (T - D - mu*(W-L))

def accelerationOnGroundLanding(Airplane):
    W = AirplaneWeight(Airplane)
    T = AirplaneThrust(Airplane)
    D = LandingAirplaneDrag(Airplane)
    L = LandingAirplaneLift(Airplane)
    mu = runwayFrictionCoefficientWithBrakes

    return g/W * (T - D - mu*(W-L))

def AirplaneThrust(Airplane):
    V = Airplane.speed
    Ts = []
    for engine in Airplane.engines:
        P = enginePower(Airplane, engine)
        etap = engine.propeller.efficiency

        Ts += [P*etap / V]

    return sum(Ts)

def enginePower(Airplane, engine):
    th = Airplane.throttle
    maxP = engine.maxPower

    return th * maxP

def allEnginesPower(Airplane):
    th = Airplane.throttle
    engines = Airplane.engines
    maxPs = [engine.maxPower for engine in engines]
    P = sum([th*maxP for maxP in maxPs])

    return P

def AirplaneDrag(Airplane):
    q = AirplaneDynamicPressure(Airplane)
    S = WingPlanformArea(Airplane)
    CD = DragCoefficient(Airplane)

    return q * S * CD

def TakeoffAirplaneDrag(Airplane):
    q = AirplaneDynamicPressure(Airplane)
    S = WingPlanformArea(Airplane)
    CD = TakeoffDragCoefficient(Airplane)

    return q * S * CD

def LandingAirplaneDrag(Airplane):
    q = AirplaneDynamicPressure(Airplane)
    S = WingPlanformArea(Airplane)
    CD = LandingDragCoefficient(Airplane)

    return q * S * CD

def WingPlanformArea(Airplane):
    b = wing.span
    c = wing.chord

    return b * c

def ParasiteDrag(Airplane, Mission, missionSegment): # FIXME: not working
    altitude = Airplane.altitude
    rho = densityAtAltitude(altitude)
    V = Airplane.speed
    mu = dynamicViscosityAtAltitude(altitude)
    Sref = WingPlanformArea(Airplane)
    CD0miscFactor = Airplane.miscellaneousParasiteDragFactor

    def componentDragContribution(component):
        FFi = component.formFactor
        Qi = component.interferenceFactor
        Cfi = ComponentSkinFrictionCoefficient(Airplane, Component)
        Sweti = component.wettedArea

        return FFi * Qi * Cfi * Sweti / Sref

    CD0Prediction = sum([componentDragContribution(component) for component in Airplane.components])

    return CD0Prediction * (1+CD0miscFactor)

def ComponentSkinFrictionCoefficient(Airplane, Component):
    rho = densityAtAltitude(Airplane.altitude)
    mu = dynamicViscosityAtAltitude(Airplane.altitude)
    V = Airplane.speed
    L = Component.referenceLength

    Re = rho * V * L / mu
    return 0.455 / (log10(Re)**2.58) # TODO: better approximation?

def InducedDrag(Airplane):
    CL = LiftCoefficient(Airplane)
    AR = Airplane.aspectRatio
    e = Airplane.oswaldEfficiencyFactor

    return CL**2 / (pi * AR * e)

def TakeoffInducedDrag(Airplane):
    CL = Airplane.takeoffLiftCoefficient
    AR = Airplane.aspectRatio
    e = Airplane.oswaldEfficiencyFactor

    return CL**2 / (pi * AR * e)

def LandingInducedDrag(Airplane):
    CL = Airplane.landingLiftCoefficient
    AR = Airplane.aspectRatio
    e = Airplane.oswaldEfficiencyFactor

    return CL**2 / (pi * AR * e)

def DragCoefficient(Airplane):
    CD0 = ParasiteDrag(Airplane, Mission, missionSegment)
    CDi = InducedDrag(Airplane)
    CDc = Airplane.compressibilityDrag

    return CD0 + CDi + CDc

def TakeoffDragCoefficient(Airplane):
    CD0 = ParasiteDrag(Airplane, Mission, missionSegment)
    CDi = TakeoffInducedDrag(Airplane)
    CDc = Airplane.compressibilityDrag

    return CD0 + CDi + CDc

def LandingDragCoefficient(Airplane):
    CD0 = ParasiteDrag(Airplane, Mission, missionSegment)
    CDi = LandingInducedDrag(Airplane)
    CDc = Airplane.compressibilityDrag

    return CD0 + CDi + CDc

def SteadyLevelFlightLiftCoefficient(Airplane):
    qinf = AirplaneDynamicPressure(Airplane)
    W = AirplaneWeight(Airplane)
    S = WingPlanformArea(Airplane)

    return W / (qinf * S)

def AirplaneLift(Airplane):
    q = AirplaneDynamicPressure(Airplane)
    S = WingPlanformArea(Airplane)
    CL = LiftCoefficient(Airplane)

    return q * S * CL

def TakeoffAirplaneLift(Airplane):
    q = AirplaneDynamicPressure(Airplane)
    S = WingPlanformArea(Airplane)
    CL = Airplane.takeoffLiftCoefficient

    return q * S * CL

def LandingAirplaneLift(Airplane):
    q = AirplaneDynamicPressure(Airplane)
    S = WingPlanformArea(Airplane)
    CL = Airplane.landingLiftCoefficient

    return q * S * CL

def climbRangeCredit(Airplane, tstep):
    rangeRate = climbRangeRate(Airplane)

    return rangeRate * tstep

def climbRangeRate(Altitude, tstep):
    climbRate = climbAltitudeRate(Airplane)
    flightPathAngle = Airplane.flightPathAngle

    return climbRate / tan(flightPathAngle)

def climbAltitudeCredit(Airplane, tstep):
    climbRate = climbAltitudeRate(Airplane)

    return climbRate * tstep

def climbAltitudeRate(Airplane):
    excessPower = maxExcessPower(Airplane)
    W = AirplaneWeight(Airplane)

    return excessPower / W

def maxExcessPower(Airplane):
    Vguess = Airplane.speed
    def functionToMinimize(V):
        A = copy.deepcopy(Airplane) # make sure we're not messing stuff up
        A.speed = V # allow the sub-calculations to use the speed passed in

        return powerAvailableAtAltitude(A) - PowerRequiredAtAltitude(A)

    return minimize(functionToMinimize, [Vguess])

def powerAvailableAtAltitude(Airplane):
    TAalt = thrustAvailableAtAlitude(Airplane)
    V = Airplane.speed

    return TAalt * V

def thrustAvailableAtAlitude(Airplane):
    ct = coefficientOfThrust(Airplane)
    rhoAlt = densityAtAltitude(Airplane.altitude)
    n = Airplane.engine.PmaxRotationRate
    d = Airplane.propeller.diameter

    return ct * rhoAlt * n**2 * d ** 4

def coefficientOfThrust(Airplane):
    cp = coefficientOfPower(Airplane)
    etap = Airplane.propeller.efficiency
    V = Airplane.speed

    return cp * etap / V

def coefficientOfPower(Airplane):
    Peng = allEnginesPower(Airplane)
    rhoAlt = densityAtAltitude(Airplane.altitude)
    n = Airplane.engine.PmaxRotationRate
    d = Airplane.propeller.diameter

    return Peng / ( rhoAlt * n**3 * d**5 )


def powerRequiredAtAltitude(Airplane):
    PRSL = powerRequiredAtSeaLevel(Airplane)
    rhoSL = densityAtAltitude(0)
    rhoAlt = densityAtAltitude(Airplane.altitude)

    return PRSL * (rhoAlt / rhoSL)

def powerRequiredAtSeaLevel(Airplane):
    TRSL = thrustRequiredAtSeaLevel(Airplane)
    V = Airplane.speed

    return TRSL * V

def thrustRequiredAtSeaLevel(Airplane):
    LoD = currentLiftOverDrag(Airplane)
    W = AirplaneWeight(Airplane)

    return W / LoD

def currentLiftOverDrag(Airplane):
    CL = SteadyLevelFlightLiftCoefficient(Airplane)
    CD = DragCoefficient(Airplane)

    return CL/CD

def climbVelocity(Airplane):
    flightPathAngle = Airplane.flightPathAngle
    climbRate = climbAltitudeRate(Airplane)

    return climbRate / sin(flightPathAngle)

################################################################################
# UPDATING FUNCTIONS
################################################################################

def updateFuel(Airplane, tstep):
    P = allEnginesPower(Airplane)
    E = P*tstep
    gas = Airplane.powerplant.gas
    battery = Airplane.powerplant.battery
    mg = gas.mass if gas is not None else 0
    mb = battery.mass if battery is not None else 0
    generator = Airplane.powerplant.generator
    percentElectric = Airplane.powerplant.percentElectric
    generatorOn = Airplane.powerplant.generatorOn

    Eb = E*percentElectric # energy requested of battery
    Eg = E*(1-percentElectric) + (generator.power*tstep*generator.efficiency if generatorOn else 0) # energy requested of gas

    if battery is not None:
       battery.energy -= Eb
    if gas is not None:
        gas.mass -= Eg/gas.energyDensity
