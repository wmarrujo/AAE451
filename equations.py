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

def AccelerationOnTakeoff(airplane):
    W = AirplaneWeight(airplane)
    T = AirplaneThrust(airplane)
    D = AirplaneDrag(airplane)
    L = AirplaneLift(airplane)
    mu = runwayFrictionCoefficientNoBrakes
    
    F = T - D - mu*(W-L)
    m = W/g
    return F/m

def AccelerationOnLanding(airplane):
    W = AirplaneWeight(airplane)
    T = AirplaneThrust(airplane)
    D = AirplaneDrag(airplane)
    L = AirplaneLift(airplane)
    mu = runwayFrictionCoefficientWithBrakes
    
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
    S = airplane.wing.planformArea
    CD = DragCoefficient(airplane)
    
    return q * S * CD

def ParasiteDragCoefficient(airplane):
    Sref = airplane.wing.planformArea
    CD0miscFactor = airplane.miscellaneousParasiteDragFactor
    
    def componentDragContribution(component):
        FFi = component.formFactor(airplane)
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

def InducedDragCoefficient(airplane):
    CL = LiftCoefficient(airplane)
    AR = airplane.wing.aspectRatio
    e = airplane.oswaldEfficiencyFactor
    
    return CL**2 / (pi * AR * e)

def DragCoefficient(airplane):
    CD0 = ParasiteDragCoefficient(airplane)
    CDi = InducedDragCoefficient(airplane)
    CDc = airplane.compressibilityDragCoefficient
    
    return CD0 + CDi + CDc

def LiftCoefficient(airplane):
    a = airplane.angleOfAttack
    CL = airplane.wing.airfoil.liftCoefficientAtAngleOfAttack(a)
    
    return CL

def AirplaneLift(airplane):
    q = AirplaneDynamicPressure(airplane)
    S = airplane.wing.planformArea
    CL = LiftCoefficient(airplane)
    
    return q * S * CL

@memoize
def MaximumLiftOverDragAngleOfAttack(airplane):
    amin = airplane.wing.airfoil.minimumDefinedAngleOfAttack
    amax = airplane.wing.airfoil.maximumDefinedAngleOfAttack
    
    aguess = airplane.angleOfAttack
    
    def functionToMinimize(X):
        A = copy.deepcopy(airplane)
        A.flightPathAngle = 0
        A.pitch = X[0]
        
        L = AirplaneLift(A)
        D = AirplaneDrag(A)
        
        return -L/D
    
    result = minimize(functionToMinimize, [aguess], bounds=[(amin, amax)], method="slsqp")
    a = result["x"][0]
    
    return a

def MaximumLiftOverDragVelocity(airplane):
    # Vguess = airplane.speed
    #
    # def functionToMinimize(X):
    #     A = copy.deepcopy(airplane)
    #     A.speed = X[0]
    #
    #     L = AirplaneLift(A)
    #     D = AirplaneDrag(A)
    #
    #     return -L/D
    #
    # result = minimize(functionToMinimize, [Vguess], bounds=[(0, None)])
    # V = result["x"][0]
    #
    # return V
    
    # TODO: verify that this equation works (Raymer 2018 equation 17.10)
    rho = densityAtAltitude(airplane.altitude)
    CL = LiftCoefficient(airplane)
    W = AirplaneWeight(airplane)
    S = airplane.wing.planformArea
    
    return sqrt(2 / (rho * CL) * (W/S))

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

def AirplaneSpecificFuelConsumption(airplane):
    pass # TODO: implement, then use in UseFuel function

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

def MinimumPowerSpeed(airplane):
    W = AirplaneWeight(airplane)
    S = airplane.wing.planformArea
    rho = densityAtAltitude(airplane.altitude)
    CD0 = ParasiteDragCoefficient(airplane)
    AR = airplane.wing.aspectRatio
    e = airplane.oswaldEfficiencyFactor
    
    return sqrt(2/rho * W/S * sqrt(1 / (3 * CD0 * pi * AR * e)))

def BestRateOfClimbSpeed(airplane):
    W = AirplaneWeight(airplane)
    S = airplane.wing.planformArea
    rho = densityAtAltitude(airplane.altitude)
    CD0 = ParasiteDragCoefficient(airplane)
    AR = airplane.wing.aspectRatio
    e = airplane.oswaldEfficiencyFactor
    
    return sqrt(2/rho * W/S * sqrt(1 / (CD0 * pi * AR * e)))

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

def UpdateWaiting(airplane, t, tstep):
    UpdateFuel(airplane, tstep)

def UpdateTakeoff(airplane, t, tstep): # see Raymer-v6 section 17.8.1
    acceleration = AccelerationOnTakeoff(airplane) # find acceleration from thrust, drag and ground friction
    airplane.speed += acceleration * tstep # update speed with acceleration
    airplane.position += airplane.speed * tstep # update position with speed
    UpdateFuel(airplane, tstep) # update the fuel

def UpdateClimb(airplane, t, tstep):
    T = AirplaneThrust(airplane)
    D = AirplaneDrag(airplane)
    W = AirplaneWeight(airplane)
    gamma = arcsin((T-D)/W)
    VminP = MinimumPowerSpeed(airplane)
    #throttle =  (MaxEnginePower / lapseRate )
    # TODO: determine throttle to keep this condition (that way fuel usage will be correct)
    
    airplane.flightPathAngle = gamma
    airplane.pitch = gamma
    airplane.speed = VminP
    airplane.altitude += VminP * sin(gamma) * tstep
    airplane.position += VminP * cos(gamma) * tstep
    UpdateFuel(airplane, tstep)

def UpdateCruise(airplane, t, tstep):
    VbestR = BestRateOfClimbSpeed(airplane)
    
    airplane.speed = VbestR
    airplane.position += VbestR * tstep
    UpdateFuel(airplane, tstep)

def UpdateDescent(airplane, t, tstep):
    gamma = arctan2(convert(-1000, "ft", "m"), convert(3, "nmi", "m")) # using "rule of threes" (for passenger comfort) - glide ratio of 3nmi per 1000ft of descent
    VminP = MinimumPowerSpeed(airplane)
    # TODO: update throttle setting
    
    airplane.flightPathAngle = gamma
    airplane.pitch = gamma
    airplane.speed = VminP
    airplane.altitude += VminP * sin(gamma) * tstep
    airplane.position += VminP * cos(gamma) * tstep
    UpdateFuel(airplane, tstep)

def UpdateLanding(airplane, t, tstep):
    acceleration = AccelerationOnLanding(airplane) # find acceleration from thrust, drag and ground friction
    airplane.speed += acceleration * tstep # update speed with acceleration
    airplane.position += airplane.speed * tstep # update position with speed
    
    UpdateFuel(airplane, tstep) # update the fuel
