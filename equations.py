# LOCAL DEPENDENCIES

from utilities import *

from constants import *
from parameters import *

# EXTERNAL DEPENDENCIES

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
    
    return mf*g

def EmptyWeight(airplane):
    W0 = airplane.initialGrossWeight
    
    return convert(2000, "lb", "N") # TODO: temporary, replace with component weight buildup later

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
    Re = 10 if Re <= 10 else Re # make sure log10 has a value
    
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

def GetCoefficientOfLiftForSteadyLevelFlight(airplane):
    W = AirplaneWeight(airplane)
    q = AirplaneDynamicPressure(airplane)
    S = airplane.wing.planformArea
    
    return W / (q * S)

def GetAngleOfAttackForSteadyLevelFlight(airplane):
    cl = GetCoefficientOfLiftForSteadyLevelFlight(airplane)
    f = functionFromPairs(pairsFromColumns(airplane.wing.airfoil.data, "CL", "alpha")) # FIXME: dangerous, because it's not a function in this direction
    
    a = f(cl)
    
    if a is not None:
        return convert(a, "deg", "rad")
    else:
        return None

def ThrustRequiredAtSeaLevelForSteadyLevelFlight(airplane):
    CL = LiftCoefficient(airplane)
    CD = DragCoefficient(airplane)
    W = AirplaneWeight(airplane)
    
    return W / (CL/CD)

def PowerRequiredAtSeaLevelForSteadyLevelFlight(airplane):
    TRsl = ThrustRequiredAtSeaLevelForSteadyLevelFlight(airplane)
    V = airplane.speed
    
    return TRsl * V

def PowerRequiredAtAltitudeForSteadyLevelFlight(airplane):
    PRsl = PowerRequiredAtSeaLevelForSteadyLevelFlight(airplane)
    rhoAlt = densityAtAltitude(airplane.altitude)
    rhoSL = densityAtAltitude(0)
    
    return PRsl * (rhoAlt / rhoSL)

def PowerAvailableAtAlittudeForSteadyLevelFlight(airplane):
    TAalt = AirplaneThrust(airplane)
    V = airplane.speed
    
    return TAalt * V

def ExcessPowerAtAltitudeForSteadyLevelFlight(airplane):
    PAalt = PowerAvailableAtAlittudeForSteadyLevelFlight(airplane)
    PRalt = PowerRequiredAtAltitudeForSteadyLevelFlight(airplane)
    
    return PAalt - PRalt

def VelocityForMaximumExcessPower(airplane):
    Vguess = airplane.speed
    Vstall = StallSpeed(airplane)
    
    def functionToMinimize(X):
        A = copy.deepcopy(airplane)
        A.speed = X[0]
        A.flightPathAngle = 0
        A.pitch = GetAngleOfAttackForSteadyLevelFlight(A)
        if A.pitch is None: # CL is too high for steady level flight
            EP = float("inf") # pseudo bound to minimizer
        else:
            EP = ExcessPowerAtAltitudeForSteadyLevelFlight(A)
        
        return -EP
    
    result = minimize(functionToMinimize, [Vguess], bounds = [(Vstall, None)], tol=1e0) # tolerance set pretty high because it doesn't need to be that accurate
    V = result["x"][0]
    
    return V

def MaximumLiftOverDragVelocity(airplane):
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
# COST FUNCTIONS
################################################################################

# This is based on the DAPCA IV model in Raymer v6 Ch. 18.4.2
# DAPCA assumes all aluminum framing, but provides fudge factors to adjust hour calculations

def EngineeringHours(airplane):
    We = airplane.emptyWeight / g # DAPCA model needs empty weight in [kgs]
    V = None  # Maximum velocity [km/h]
    Q = Aiplane.productionQuantityNeeded
    
    return 5.18 * (We**0.777) * (V**0.894) * (Q**0.163)

def ToolingHours(airplane):
    We = airplane.emptyWeight / g # DAPCA model needs empty weight in [kgs]
    V = None  # Maximum velocity [km/h]
    Q = Aiplane.productionQuantityNeeded
    
    return 7.22 * (We**0.777) * (V**0.696) * (Q**0.263)

def ManufacturingHours(airplane):
    We = airplane.emptyWeight / g # DAPCA model needs empty weight in [kgs]
    V = None  # Maximum velocity [km/h]
    Q = Aiplane.productionQuantityNeeded
    
    return 10.5 * (We**0.82) * (V**0.484) * (Q**0.641)

def QualityControlHours(airplane):
    mfgHours = ManufacturingHours(airplane)
    
    return 0.133 * mfgHours

def DevelopmentSupportCost(airplane):
    We = airplane.emptyWeight / g # DAPCA model needs empty weight in [kgs]
    V = None  # Maximum velocity [km/h]
    iR = inflation2012to2019
    
    return iR * 67.4 * (We**0.630) * (V**1.3)

def FlightTestCost(airplane):
    We = airplane.emptyWeight / g # DAPCA model needs empty weight in [kgs]
    V = None  # Maximum velocity [km/h]
    FTA = airplane.numberFlightTestAircraft
    iR = inflation2012to2019
    
    return iR * 1947 * (We**0.325) * (V**0.822) * (FTA**1.21)

def ManufacturingMaterialsCost(airplane):
    We = airplane.emptyWeight / g # DAPCA model needs empty weight in [kgs]
    V = None  # Maximum velocity [km/h]
    Q = Aiplane.productionQuantityNeeded
    iR = inflation2012to2019
    
    return iR * 31.2 * (We**0.921) * (V**0.621) * (Q**0.799)

def PassengerAdditionalCost(airplane):
    N = airplane.passengers
    P = airplane.pilot
    Cp = generalAviationPassengerCostFactor
    iR = inflation2012to2019
    
    return Cp * iR * (N + P)

################################################################################
# PREDICTION FUNCTIONS
################################################################################

def PredictWingMass(span, aspectRatio, chord, loadFactor, sweep, taperRatio, planformArea, airplaneGrossWeight, airplaneFuelWeight, cruiseDynamicPressure, thicknessToChordRatio):
    b = span
    AR = aspectRatio
    c = chord
    S = convert(planformArea, "m^2", "ft^2")
    L = sweep
    lambd = taperRatio
    Nz = loadFactor
    W0 = convert(airplaneGrossWeight, "N", "lb")
    Wf = convert(airplaneFuelWeight, "N", "lb")
    q = convert(cruiseDynamicPressure, "N/m^2", "lb/ft^2")
    tc = thicknessToChordRatio
    
    Wfw = Wf/2 # fuel weight per wing
    Ww = 0.036*S**0.758 * Wfw**0.0035 * (AR / cos(L)**2)**0.6 * q**0.006 * lambd**0.04 * (100 * tc / cos(L))**-0.3 * (Nz * W0)**0.49
    return convert(Ww, "lb", "N") / g

def PredictFuselageMass(wettedArea, airplaneGrossWeight, length, diameter, cruiseDynamicPressure, pressurizationWeightPenalty, loadFactor):
    Sf = convert(wettedArea, "m^2", "ft^2")
    W0 = convert(airplaneGrossWeight, "N", "lb")
    Lt = convert(length, "m^2", "ft^2")
    d = convert(diameter, "m", "ft")
    q = convert(cruiseDynamicPressure, "N/m^2","lb/ft^2")
    Wp = convert(pressurizationWeightPenalty, "N", "lb")
    Nz = loadFactor
    
    LD = Lt/d
    Wf = 0.052 * Sf**1.086 * (Nz*W0)**0.177 * Lt**(-0.051) * LD**(-0.072) * q**0.241 + Wp # RAYMER eqn 15.48
    return convert(Wf, "lb", "N")/g

def PredictHorizontalStabilizerMass(airplaneGrossWeight, loadFactor, taperRatio, sweep, wingTaperRatio, horizontalTailVolumeCoefficient, wingSpan, wingChord, dt, cruiseDynamicPressure, wingThicknessToChordRatio):
    W0 = convert(airplaneGrossWeight, "N", "lb")
    Nz = loadFactor
    lambdaHT = taperRatio
    LHT = sweep
    lambd = wingTaperRatio
    ch = horizontalTailVolumeCoefficient
    b = wingSpan
    c = wingChord
    dt = dt # FIXME: what is dt? replace with complete name for right side of equals, and in function definition above
    q = convert(cruiseDynamicPressure, "N/m^2", "lb/ft^2")
    tc = wingThicknessToChordRatio
    
    AR = b/c
    Sht = convert(ch * (b * c / dt), "m^2", "ft^2") # FIXME: move to airplane definition
    WHT = 0.016 * (Nz*W0)**0.414 * q**0.168 * Sht**0.896 * (100 * tc / cos(lambd))**-0.12 * (AR / cos(LHT)**2)**0.043 * lambdaHT**-0.02
    return convert(WHT, "lb", "N")/g

def PredictVerticalStabilizerMass(taperRatio, sweep, loadFactor, verticalTailPosition, airplaneGrossWeight, cruiseDynamicPressure, verticalTailVolumeCoefficient, dv, wingSpan, wingChord, wingPlanformArea, wingThicknessToChordRatio):
    lambdaVT = taperRatio
    LVT = sweep
    Nz = loadFactor
    HtHv = verticalTailPosition # 0 for conventional, 1 for T-tail
    W0 = convert(airplaneGrossWeight, "N", "lb")
    q = convert(cruiseDynamicPressure, "N/m^2", "lb/ft^2")
    cv = verticalTailVolumeCoefficient
    dv = dv # FIXME: what is dv? replace with complete name for right side of equals, and in function definition above
    bw = wingSpan
    Sw = wingPlanformArea
    tc = wingThicknessToChordRatio
    
    S = convert(cv * (Sw * bw / dv), "m^2", "ft^2") # FIXME: move to airplane definition
    AR = wingSpan / wingChord
    WVT = 0.073 * (1 + 0.2*HtHv) * (Nz * W0)**0.376 * q**0.122 * S**0.873 * (100 * tc / cos(LVT))**-0.49 * (AR / cos(LVT)**2) * lambdaVT**0.039
    return convert(WVT, "lb", "N")/g

def PredictInstalledEngineMass(uninstalledEngineMass, numberOfEngines):
    mU = convert(uninstalledEngineMass, "N", "lb")
    N = numberOfEngines
    
    Weng = 2.575 * mU**0.922 * N
    return convert(Weng, "lb", "N")

def PredictMainGearMass(airplaneGrossWeight, landingLoadFactor, length):
    Wl = convert(airplaneGrossWeight, "N", "lb")
    Nz = landingLoadFactor
    Lm = convert(length, "m", "in") # FIXME: you sure this isn't ft?
    
    Wmg = 0.095 * (Nz * Wl)**0.768 * (Lm/12)**0.409
    return convert(Wmg, "lb", "N")/g

def PredictFrontGearMass(airplaneGrossWeight, landingLoadFactor, length):
    Wl = convert(airplaneGrossWeight, "N", "lb")
    Nz = landingLoadFactor
    Ln = convert(length, "m", "in") # FIXME: you sure this isn't ft?
    
    Wng = 0.125 * (Nz * Wl)**0.566 * (Ln/12)**0.845
    return convert(Wng, "lb", "N")/g

def PredictFuelSystemMass(totalFuelVolume, dropTanksVolume, numberOfFuelTanks, numberOfEngines):
    Vt = convert(totalFuelVolume, "m^3", "gal")
    Vd = convert(dropTanksVolume, "m^3", "gal")
    Nt = numberOfFuelTanks
    Neng = numberOfEngines
    
    Vi = Vt - Vd
    Wfs = 2.49 * Vt**0.726 * (1 / (Vi/Vt))**0.363 * Nt**0.242 * Neng**0.157
    return convert(Wfs, "lb", "N")/g

def PredictFlightControlsMass(fuselageLength, wingSpan, loadFactor, airplaneGrossWeight):
    Lf = convert(fuselageLength, "m", "ft")
    b = convert(wingSpan, "m", "ft")
    Nz = loadFactor
    W0 = convert(airplaneGrossWeight, "N", "lb")
    
    Wfc = 0.053 * Lf**1.536 * b**0.371 * (Nz * W0 * 10**-4)**0.80
    return convert(Wfc, "lb", "N")/g

def PredictHydraulicsMass(airplaneGrossWeight):
    W0 = airplaneGrossWeight
    
    return 0.001*W0/g

def PredictAvionicsMass(uninstalledAvionicsWeight):
    WU = convert(uninstalledAvionicsWeight, "N", "lb")
    
    W = 2.117 * WU**0.933
    return convert(W, "lb", "N")/g

def PredictElectronicsMass(fuelSystemMass, installedAvionicsMass):
    Wfs = convert(fuelSystemMass * g, "N", "lb")
    Wavi = convert(installedAvionicsMass * g, "N", "lb")
    
    Welec = 12.57 * (Wfs + Wavi)**0.51
    return convert(Welec, "lb", "N")/g

def PredictAirConIceMass(airplaneGrossWeight, peopleLoaded, installedAvionicsMass, cruiseMachNumber):
    W0 = convert(airplaneGrossWeight, "N", "lb")
    Np = peopleLoaded
    Wavi = convert(installedAvionicsMass * g, "N", "lb")
    M = cruiseMachNumber
    
    Waci = 0.265 * W0**0.52 * Np**0.68 * Wavi**0.17 * M**0.08
    return convert(Waci, "lb", "N")/g

def PredictFurnishingsMass(airplaneGrossWeight):
    W0 = convert(airplaneGrossWeight, "N", "lb")
    
    W = 0.0582 * W0 - 65
    return convert(W, "lb", "N")/g

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
    # unset to calculate for steady level flight
    airplane.flightPathAngle = 0
    airplane.pitch = 0
    W = AirplaneWeight(airplane)
    V = VelocityForMaximumExcessPower(airplane)
    
    airplane.speed = V
    airplane.pitch = GetAngleOfAttackForSteadyLevelFlight(airplane)
    
    ExcessPower = ExcessPowerAtAltitudeForSteadyLevelFlight(airplane)
    climbRate = ExcessPower / W
    
    airplane.flightPathAngle = arcsin(climbRate / V)
    airplane.pitch = airplane.flightPathAngle + airplane.pitch # make it the angle of attack we're talking about
    airplane.altitude += V * sin(airplane.flightPathAngle) * tstep
    airplane.position += V * cos(airplane.flightPathAngle) * tstep

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
