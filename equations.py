# LOCAL DEPENDENCIES

from utilities import *

from constants import *
from parameters import *

# EXTERNAL DEPENDENCIES

from scipy import *
from scipy.optimize import minimize, root
import copy
from matplotlib.pyplot import *

################################################################################
# INFORMATION FUNCTIONS
################################################################################

def AirplaneWeight(airplane): # TODO: calculate with airplane.mass?
    Wpay = PayloadWeight(airplane)
    Wfuel = FuelWeight(airplane)
    Wempty = airplane.emptyMass * g

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
    We = g * sum([comp.mass for comp in airplane.components])

    return We # TODO: temporary, replace with component weight buildup later

def CenterGravity(airplane):
    moment = sum([(comp.x * comp.mass*g) for comp in airplane.components])
    moment += airplane.powerplant.gas.mass*g * airplane.wing.x
    moment += sum([pay.x * pay.mass*g for pay in airplane.payloads])
    W = AirplaneWeight(airplane)

    return moment / W

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

    result = minimize(functionToMinimize, [aguess], bounds=[(amin, amax)])
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

def PowerAvailableAtAltitudeForSteadyLevelFlight(airplane):
    TAalt = AirplaneThrust(airplane)
    V = airplane.speed

    return TAalt * V

def ExcessPowerAtAltitudeForSteadyLevelFlight(airplane):
    PAalt = PowerAvailableAtAltitudeForSteadyLevelFlight(airplane)
    PRalt = PowerRequiredAtAltitudeForSteadyLevelFlight(airplane)

    return PAalt - PRalt

def VelocityForMaximumExcessPower(airplane):
    Vguess = airplane.speed
    VTO = TakeoffSpeed(airplane)

    def functionToMinimize(X):
        A = copy.deepcopy(airplane)
        A.speed = X[0]
        A.flightPathAngle = 0
        A.pitch = GetAngleOfAttackForSteadyLevelFlight(A)
        if A.pitch is None: # CL is too high for steady level flight
            EP = -1e10 # pseudo bound to minimizer
        else:
            EP = ExcessPowerAtAltitudeForSteadyLevelFlight(A)
            if EP < 0: # cannot fly
                EP = -1e10 # pseudo bound to minimizer

        return -EP

    result = minimize(functionToMinimize, [Vguess], bounds = [(VTO, None)], tol=1e0) # tolerance set pretty high because it doesn't need to be that accurate
    V = result["x"][0]

    return V

def MaximumLiftOverDragVelocity(airplane):
    # TODO: verify that this equation works (Raymer 2018 equation 17.10)
    rho = densityAtAltitude(airplane.altitude)
    CL = LiftCoefficient(airplane)
    W = AirplaneWeight(airplane)
    S = airplane.wing.planformArea

    return sqrt(2 / (rho * CL) * (W/S))

def CarsonVelocity(airplane):
    VminLD = MaximumLiftOverDragVelocity(airplane)

    return 1.3 * VminLD

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

def MaximumSteadyLevelFlightSpeed(airplane):

    Vhguess = convert(200, "kts", "m/s")

    def functionToFindRootOf(X):
        A = copy.deepcopy(airplane)
        A.speed = X[0]
        A.throttle = 1
        A.altitude = cruiseAltitude
        A.flightPathAngle = 0
        A.pitch = GetAngleOfAttackForSteadyLevelFlight(A)
        if A.pitch is None:
            EP = -1e10
        else:
            EP = ExcessPowerAtAltitudeForSteadyLevelFlight(A)

        return EP

    X0 = [Vhguess]
    result = root(functionToFindRootOf, X0, tol=1e-2)
    Xf = result["x"]
    Vh = Xf[0]

    return Vh

################################################################################
# PRODUCTION COST FUNCTIONS
################################################################################

def EngineeringHours(airplane, plannedAircraft):
    Waf = 0.65*convert(EmptyWeight(airplane), "N", "lb")
    Vh = convert(MaximumSteadyLevelFlightSpeed(airplane), "m/s", "kts")
    N = plannedAircraft
    Fcert = certFudge
    Fcf = flapFudge
    Fcomp = 1 + airplane.compositeFraction
    Fpress = pressFudge

    print(Vh)
    print(Waf/0.65)

    return 0.0396 * (Waf**0.791) * (Vh**1.526) * (N**0.183) * Fcert * Fcf * Fcomp * Fpress

def ToolingHours(airplane, plannedAircraft):
    Waf = 0.65*convert(EmptyWeight(airplane), "N", "lb")
    Vh = convert(MaximumSteadyLevelFlightSpeed(airplane), "m/s", "kts")
    N = plannedAircraft
    Qm = plannedAircraft/60
    Ftaper = taperFudge
    Fcf = flapFudge
    Fcomp = 1 + airplane.compositeFraction
    Fpress = pressFudge

    return 1.0032 * (Waf**0.764) * (Vh**0.899) * (N**0.178) * (Qm**0.066) * Ftaper * Fcf * Fcomp * Fpress

def ManufacturingHours(airplane, plannedAircraft):
    Waf = 0.65*convert(EmptyWeight(airplane), "N", "lb")
    Vh = convert(MaximumSteadyLevelFlightSpeed(airplane), "m/s", "kts")
    N = plannedAircraft
    Fcert = certFudge
    Fcf = flapFudge
    Fcomp = 1 + 0.25*airplane.compositeFraction

    return 9.6613 * (Waf**0.74) * (Vh**0.543) * (N**0.524) * Fcert * Fcf * Fcomp

def EngineeringCost(airplane, plannedAircraft):
    Heng = EngineeringHours(airplane, plannedAircraft)
    Reng = engineeringLaborRate
    CPI = inflation2012to2019

    return 2.0969 * Heng * Reng * CPI

def DevelopmentalSupportCost(airplane):
    Waf = 0.65*convert(EmptyWeight(airplane), "N", "lb")
    Vh = convert(MaximumSteadyLevelFlightSpeed(airplane), "m/s", "kts")
    Np = numberFlightTestAircraft
    Fcert = certFudge
    Fcf = flapFudge
    Fcomp = 1 + 0.5*airplane.compositeFraction
    Fpress = pressFudge
    CPI = inflation2012to2019

    return 0.06458 * (Waf**0.873) * (Vh**1.89) * (Np**0.346) * Fcert * Fcf * Fcomp * Fpress * CPI

def FlightTestCost(airplane):
    Waf = 0.65*convert(EmptyWeight(airplane), "N", "lb")
    Vh = convert(MaximumSteadyLevelFlightSpeed(airplane), "m/s", "kts")
    Np = numberFlightTestAircraft
    CPI = inflation2012to2019
    Fcert = certFudge

    return 0.009646 * (Waf**1.16) * (Vh**1.3718) * (Np**1.281) * CPI * Fcert

def ToolingCost(airplane, plannedAircraft):
    Htool = ToolingHours(airplane, plannedAircraft)
    Rtool = toolingLaborRate
    CPI = inflation2012to2019

    return 2.0969 * Htool * Rtool * CPI

def ManufacturingCost(airplane, plannedAircraft):
    Hmfg = ManufacturingHours(airplane, plannedAircraft)
    Rmfg = manufacturingLaborRate
    CPI = inflation2012to2019
    N = plannedAircraft

    return (2.0969 * Hmfg * Rmfg * CPI) / N

def QualityControlCost(airplane, plannedAircraft):
    Cmfg = ManufacturingCost(airplane, plannedAircraft)
    Fcert = certFudge
    Fcomp = 1 + 0.5*airplane.compositeFraction

    return 0.13 * Cmfg * Fcert * Fcomp

def MaterialCost(airplane, plannedAircraft):
    Waf = 0.65*convert(EmptyWeight(airplane), "N", "lb")
    Vh = convert(MaximumSteadyLevelFlightSpeed(airplane), "m/s", "kts")
    N = plannedAircraft
    CPI = inflation2012to2019
    Fcert = certFudge
    Fcf = flapFudge
    Fpress = pressFudge

    return (24.896 * (Waf**0.689) * (Vh**0.624) * (N**0.762) * CPI * Fcert * Fcf * Fpress) / N

def EngineCost(airplane, engine):
    Npp = numberICEngines
    CPI = inflation2012to2019

    PSI = engine.maxPower
    Pbhp = convert(PSI, "W", "hp")

    return 174 * Npp * Pbhp * CPI

def PropellerCost(airplane):
    Npp = numberICEngines
    CPI = inflation2012to2019

    return 3145 * Npp * CPI  # For fixed pitch propeller

def PowerplantCost(airplane, engine):
    Cengine = EngineCost(airplane, engine)
    Cpropeller = PropellerCost(airplane)

    return Cengine + Cpropeller

def LandingGearCost(airplane):
    dC = -7500 if airplane.mainGear.retractable is False else 0
    CPI = inflation2012to2019

    return dC * CPI

def SeatingCost(airplane):
    num = airplane.pilots + airplane.passengers
    P = seatPrice

    return num * P

def FixedCost(airplane, plannedAircraft):
    #this is a total cost (not per aircraft)
    Ceng = EngineeringCost(airplane, plannedAircraft)
    Cdev = DevelopmentalSupportCost(airplane)
    Cft = FlightTestCost(airplane)
    Ctool = ToolingCost(airplane, plannedAircraft)

    return Ceng + Cdev + Cft + Ctool

def VariableCost(airplane, engine, plannedAircraft):
    #this is a per aircraft cost
    Cmfg = ManufacturingCost(airplane, plannedAircraft)
    Cqc = QualityControlCost(airplane, plannedAircraft)
    Cmat = MaterialCost(airplane, plannedAircraft)
    Clg = LandingGearCost(airplane)
    Cav = avionicPrice
    Cheat = cabinHeaterPrice
    Cseat = SeatingCost(airplane)
    Cmfgins = manufacturerLiabilityInsurance
    Cpp = PowerplantCost(airplane, engine)

    return Cmfg + Cqc + Cmat + Clg + Cav + Cheat + Cseat + Cmfgins + Cpp

# def ProductionCost(airplane, engine, plannedAircaft):
#
#     fixedCost = FixedCost(airplane, plannedAircraft)
#     variableCost = VariableCost(airplane, engine, plannedAircraft)
#     productionCost = (fixedCost/plannedAircraft) + variableCost
#
#     print("\nFor {:0.0f} planned aircraft".format(plannedAircraft))
#     print("Fixed Cost  = {:0.2f} USD".format(fixedCost))
#     print("Variable Cost = {:0.2f} USD/aircraft".format(variableCost))
#     print("Production Cost Per Unit = {:0.2f} USD/aircraft\n".format(productionCost))
#
#     return [fixedCost, variableCost, productionCost]

################################################################################
# OPERATING COST FUNCTIONS
################################################################################

def MaintenanceToFlightHoursRatio(airplane):
    F1 = maintF
    F2 = engineF
    F3 = 0 if airplane.mainGear.retractable is False else 0.02
    F4 = VFRF
    F5 = IFRF
    F6 = fuelF
    F7 = flapF
    F8 = certF

    return 0.30 + F1 + F2 + F3 + F4 + F5 + F6 + F7 + F8

def MaintenanceCost(airplane):
    Fmf = MaintenanceToFlightHoursRatio(airplane)
    Rap = APmechRate
    Qflgt = flightHoursYear
    CPI = inflation2012to2019

    return Fmf * Rap * Qflgt * CPI

def StorageCost(airplane):
    Rstor = monthlyStorageRate
    CPI = inflation2012to2019

    return 12 * Rstor * CPI

def AnnualFuelCost(airplane, simulation):
    ts = simulation["time"]
    ss = simulation["segment"]
    mfs = simulation["gas mass"]

    Qflgt = flightHoursYear

    # Gas Operating Cost
    mfUsedInCruise = mfs[firstIndex(ss, lambda s: s == "cruise")] - mfs[lastIndex(ss, lambda s: s == "cruise")]
    cruiseDuration = ts[lastIndex(ss, lambda s: s == "cruise")] - ts[firstIndex(ss, lambda s: s == "cruise")]
    MFR = mfUsedInCruise / cruiseDuration # mass flow rate [kg/s]
    gd = airplane.powerplant.gas.density if airplane.powerplant.gas else 0
    VFR = MFR / gd if gd != 0 else 0  # volumetric flow rate [m^3/s]

    FFcruise = 10*convert(VFR, "m^3/s", "gal/hr")  # should be in the teens, currently 1.6 gal/hr, NEEDS FIX

    Rfuel = fuelRate

    # Battery Operating Cost
    batteryCapacity = convert(airplane.powerplant.battery.capacity, "J", "kWh") if airplane.powerplant.percentElectric is not 0 else 0
    batteryPower = batteryCapacity / convert(cruiseDuration, "s", "hr") # [kW]
    Rbattery = electricityRate

    return (FFcruise * Rfuel * Qflgt) + (batteryPower * Rbattery * Qflgt)

def CrewCost(airplane):
    Ncrew = airplane.pilots
    Rcrew = pilotRate
    Qflgt = flightHoursYear
    CPI = inflation2012to2019

    return Ncrew * Rcrew * Qflgt * CPI

def AnnualInsuranceCost(airplane, purchasePrice): #not a super accurate estimation
    Cac = purchasePrice
    CPI = inflation2012to2019

    return (500 * CPI) + (0.015 * Cac)

def AnnualEngineOverhaul(airplane):
    Npp = numberICEngines
    Qflgt = flightHoursYear
    CPI = inflation2012to2019

    return 5 * Npp * Qflgt * CPI

def AnnualLoanPayment(airplane, purchasePrice):
    P = purchasePrice
    i = 0.0075 # 9% APR
    n = 180 # 12 months for 15 years

    return (12 * P * i) / (1 - (1/(1+i)**n))

def TotalAnnualCost(airplane, simulation, purchasePrice):
    Cap = MaintenanceCost(airplane)
    Cstor = StorageCost(airplane)
    Cfuel = AnnualFuelCost(airplane, simulation)
    Cins = AnnualInsuranceCost(airplane, purchasePrice)
    Cinsp = inspectionCost
    Cover = AnnualEngineOverhaul(airplane)
    Cloan = AnnualLoanPayment(airplane, purchasePrice)

    return Cap + Cstor + Cfuel + Cins + Cinsp + Cover + Cloan

def CostPerFlightHour(airplane, simulation, purchasePrice):
    Cyear = TotalAnnualCost(airplane, simulation, purchasePrice)
    Qflgt = flightHoursYear

    return Cyear / Qflgt

################################################################################
# PREDICTION FUNCTIONS
################################################################################

def PredictWingMass(span, aspectRatio, chord, loadFactor, sweep, taperRatio, planformArea, airplaneGrossWeight, airplaneFuelWeight, cruiseDynamicPressure, thicknessToChordRatio, compositeYN):
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
    composite = compositeYN

    Wfw = Wf/2 # fuel weight per wing
    Ww = 0.8 * (1 + 0.35*composite)*0.036*S**0.758 * Wfw**0.0035 * (AR / cos(L)**2)**0.6 * q**0.006 * lambd**0.04 * (100 * tc / cos(L))**-0.3 * (Nz * W0)**0.49
    return convert(Ww, "lb", "N") / g

def PredictFuselageMass(wettedArea, airplaneGrossWeight, length, diameter, cruiseDynamicPressure, pressurizationWeightPenalty, loadFactor, compositeYN):
    Sf = convert(wettedArea, "m^2", "ft^2")
    W0 = convert(airplaneGrossWeight, "N", "lb")
    L = convert(length, "m", "ft")
    Lt = 0.6*convert(length, "m", "ft")
    d = convert(diameter, "m", "ft")
    q = convert(cruiseDynamicPressure, "N/m^2","lb/ft^2")
    Wp = convert(pressurizationWeightPenalty, "N", "lb")
    Nz = loadFactor
    composite = compositeYN

    LD = L/d
    Wf = (1 + 0.35*composite)*0.052 * Sf**1.086 * (Nz*W0)**0.177 * Lt**(-0.051) * LD**(-0.072) * q**0.241 + Wp # RAYMER eqn 15.48
    return convert(Wf, "lb", "N")/g

def PredictHorizontalStabilizerMass(airplaneGrossWeight, loadFactor, taperRatio, sweep, wingSweep, horizontalTailVolumeCoefficient, wingSpan, wingChord, dt, cruiseDynamicPressure, wingThicknessToChordRatio, compositeYN):
    W0 = convert(airplaneGrossWeight, "N", "lb")
    Nz = loadFactor
    lambdaHT = taperRatio
    LHT = sweep
    Lw = wingSweep
    ch = horizontalTailVolumeCoefficient
    b = wingSpan
    c = wingChord
    dt = dt # FIXME: what is dt? replace with complete name for right side of equals, and in function definition above
    q = convert(cruiseDynamicPressure, "N/m^2", "lb/ft^2")
    tc = wingThicknessToChordRatio
    composite = compositeYN

    AR = b/c
    Sht = convert(ch * (b * c * c / dt), "m^2", "ft^2") # FIXME: move to airplane definition
    # print("Horizontal Tail Area: ", Sht, " ft^2")
    WHT = (1 + 0.35*composite)*0.016 * (Nz*W0)**0.414 * q**0.168 * Sht**0.896 * (100 * tc / cos(Lw))**-0.12 * (AR / cos(LHT)**2)**0.043 * lambdaHT**-0.02
    return convert(WHT, "lb", "N")/g

def PredictVerticalStabilizerMass(taperRatio, sweep, loadFactor, tailConfig, airplaneGrossWeight, cruiseDynamicPressure, verticalTailVolumeCoefficient, distToVert, wingSpan, wingChord, wingPlanformArea, wingThicknessToChordRatio, compositeYN):
    lambdaVT = taperRatio
    LVT = sweep
    Nz = loadFactor
    HtHv = tailConfig # 0 for conventional, 1 for T-tail
    W0 = convert(airplaneGrossWeight, "N", "lb")
    q = convert(cruiseDynamicPressure, "N/m^2", "lb/ft^2")
    cv = verticalTailVolumeCoefficient
    dv = distToVert
    bw = wingSpan
    Sw = wingPlanformArea
    tc = wingThicknessToChordRatio
    composite = compositeYN

    Svt = convert(cv * (Sw * bw / dv), "m^2", "ft^2") # FIXME: move to airplane definition
    # print("Vertical Tail Area: ", Svt, " ft^2")
    AR = wingSpan / wingChord
    WVT = (1 + 0.35*composite)*0.35 * 0.073 * (1 + 0.2*HtHv) * (Nz * W0)**0.376 * q**0.122 * Svt**0.873 * (100 * tc / cos(LVT))**-0.49 * (AR / cos(LVT)**2)**0.357 * lambdaVT**0.039
    return convert(WVT, "lb", "N")/g

def PredictInstalledEngineMass(uninstalledEngineMass, numberOfEngines):
    mU = convert(uninstalledEngineMass, "N", "lb")
    N = numberOfEngines

    Weng = 1.0*2.575 * mU**0.9 * N
    return convert(Weng, "lb", "N")

def PredictMainGearMass(airplaneGrossWeight, airplaneFuelMass, landingLoadFactor, length):
    W0 = convert(airplaneGrossWeight, "N", "lb")
    Wf = convert(airplaneFuelMass * g, "N", "lb")
    Wl = W0 - 0.8 * Wf
    Nz = landingLoadFactor
    Lm = convert(length, "m", "in") # FIXME: you sure this isn't ft?

    Wmg = 0.095 * (Nz * Wl)**0.768 * (Lm/12)**0.409 # FIXME: error here
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
    Wfs = 0.9 * 2.49 * Vt**0.726 * (1 / (Vi/Vt))**0.363 * Nt**0.242 * Neng**0.157
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

    W = 0.3 * 2.117 * WU**0.933
    return convert(W, "lb", "N")/g

def PredictElectronicsMass(fuelSystemMass, installedAvionicsMass):
    Wfs = convert(fuelSystemMass * g, "N", "lb")
    Wavi = convert(installedAvionicsMass * g, "N", "lb")

    Welec = 0.65 * 12.57 * (Wfs + Wavi)**0.51
    return convert(Welec, "lb", "N")/g

def PredictAirConIceMass(airplaneGrossWeight, peopleLoaded, installedAvionicsMass, cruiseMachNumber):
    W0 = convert(airplaneGrossWeight, "N", "lb")
    Np = peopleLoaded
    Wavi = convert(installedAvionicsMass * g, "N", "lb")
    M = cruiseMachNumber

    Waci = 0.45 * 0.265 * W0**0.52 * Np**0.68 * Wavi**0.17 * M**0.08
    return convert(Waci, "lb", "N")/g

def PredictFurnishingsMass(airplaneGrossWeight):
    W0 = convert(airplaneGrossWeight, "N", "lb")

    W = 0.0582 * W0 - 65
    return convert(W, "lb", "N")/g

def CalculatePassengerPayloadMass(ariplanePassengers):
    numpax = ariplanePassengers
    Wpax = heavyPassengerWeight if numpax <= 3 else lightPassengerWeight
    mass = numpax * Wpax / g

    return mass

def CalculateBaggageMass(airplanePassengers):
    numpax = airplanePassengers
    Wbag = heavyPassengerBagWeight if numpax <= 3 else lightPassengerBagWeight
    mass = numpax * Wbag / g

    return mass

def CalculatePilotPayloadMass(airplanePilots):
    numpilots = airplanePilots
    mass = numpilots * pilotWeight / g

    return mass

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
    airplane.angleOfAttack = GetAngleOfAttackForSteadyLevelFlight(airplane)

    ExcessPower = ExcessPowerAtAltitudeForSteadyLevelFlight(airplane)
    climbRate = ExcessPower / W
    V = airplane.speed

    airplane.flightPathAngle = arcsin(climbRate / V)
    airplane.pitch = airplane.flightPathAngle + airplane.pitch # make it the angle of attack we're talking about
    airplane.altitude += V * sin(airplane.flightPathAngle) * tstep
    airplane.position += V * cos(airplane.flightPathAngle) * tstep

    UpdateFuel(airplane, tstep)

def UpdateCruise(airplane, t, tstep):
    VbestR = MaximumLiftOverDragVelocity(airplane)

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
