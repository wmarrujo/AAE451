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
    S = airplane.wing.planformArea
    CD = DragCoefficient(airplane)
    
    return q * S * CD

def ParasiteDragCoefficient(airplane):
    altitude = airplane.altitude
    rho = densityAtAltitude(altitude)
    V = airplane.speed
    mu = dynamicViscosityAtAltitude(altitude)
    Sref = airplane.wing.planformArea
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
    
    # alphas = linspace(amin, amax, num=50)
    # CLs = [airplane.wing.airfoil.liftCoefficientAtAngleOfAttack(a) for a in alphas]
    # CDs = [airplane.wing.airfoil.dragCoefficientAtAngleOfAttack(a) for a in alphas]
    # LDs = [CL/CD for CL, CD in zip(CLs, CDs)]
    # a = alphas[LDs.index(max(LDs))]
    
    aguess = airplane.angleOfAttack
    
    def functionToMinimize(a):
        A = copy.deepcopy(airplane)
        A.flightPathAngle = 0
        A.pitch = a[0]
        
        L = AirplaneLift(A)
        D = AirplaneDrag(A)
        
        return -L/D
    
    result = minimize(functionToMinimize, [aguess], bounds=[(amin, amax)])
    a = result["x"][0]
    
    return a

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
# PRODUCTION COST FUNCTIONS
################################################################################

def engineeringHours(airplane):
    Waf = 0.065* convert(airplane.emptyWeight, "N", "lb")    # need to change once compnenet weight build-up is complete
    Vh = convert(airplane.speed, "m/s", "kts")  #needs to be max level airspeed, change later
    N = plannedAircraft
    Fcert = certFudge
    Fcf = flapFudge
    Fcomp = 1 + compFraction
    Fpress = pressFudge
    
    return 0.0396 * (Waf**0.791) * (Vh**1.526) * (N**0.183) * Fcert * Fcf * Fcomp * Fpress

def toolingHours(airplane):
    Waf = 0.065* convert(airplane.emptyWeight, "N", "lb")    # need to change once compnenet weight build-up is complete
    Vh = convert(airplane.speed, "m/s", "kts") #needs to be max level airspeed, change later
    N = plannedAircraft
    Qm = plannedAircraft/60
    Ftaper = taperFudge
    Fcf = flapFudge
    Fcomp = 1 + compFraction
    Fpress = pressFudge
    
    return 1.0032 * (Waf**0.764) * (Vh**0.899) * (N**0.178) * (Qm**0.066) * Ftaper * Fcf * Fcomp * Fpress
    
def manufacturingHours(airplane):
    Waf = 0.065* convert(airplane.emptyWeight, "N", "lb")    # need to change once compnenet weight build-up is complete
    Vh = convert(airplane.speed, "m/s", "kts") #needs to be max level airspeed, change later
    N = plannedAircraft
    Fcert = certFudge
    Fcf = flapFudge
    Fcomp = 1 + 0.25*compFractionq
    
    return 9.6613 * (Waf**0.74) * (Vh**0.543) * (N**0.524) * Fcert * Fcf * Fcomp

def engineeringCost(airplane):
    Heng = engineeringHours(airplane)
    Reng = engineeringLaborRate
    CPI = inflation2012to2019
    
    return 2.0969 * Heng * Reng * CPI
    
def developmentalSupportCost(airplane):
    Waf = 0.065* convert(airplane.emptyWeight, "N", "lb")   # need to change once compnenet weight build-up is complete
    Vh = convert(airplane.speed, "m/s", "kts")  #needs to be max level airspeed, change later
    Np = numberFlightTestAircraft
    Fcert = certFudge
    Fcf = flapFudge
    Fcomp = 1 + 0.5*compFraction
    Fpress = pressFudge
    
    return 0.06458 * (Waf**0.873) * (Vh**1.89) * (Np**0.346) * Fcert * Fcf * Fcomp * Fpress
    
def flightTestCost(airplane):
    Waf = 0.065* convert(airplane.emptyWeight, "N", "lb")    # need to change once compnenet weight build-up is complete
    Vh = convert(airplane.speed, "m/s", "kts") #needs to be max level airspeed, change later
    Np = numberFlightTestAircraft
    CPI = inflation2012to2019
    Fcert = certFudge

    return 0.009646 * (Waf**1.16) * (Vh**1.3718) * (Np**1.281) * CPI * Fcert
    
def toolingCost(airplane):
    Htool = toolingHours(airplane)
    Rtool = toolingLaborRate
    CPI = inflation2012to2019
    
    return 2.0969 * Htool * Rtool * CPI
    
def manufacturingCost(airplane):
    Hmfg = manufacturingHours(airplane)
    Rmfg = manufacturingLaborRate
    CPI = inflation2012to2019
        
    return 2.0969 * Hmfg * Rmfg * CPI
    
def qualityControlCost(airplane):
    Cmfg = manufacturingCost(airplane)
    Fcert = certFudge
    Fcomp = compFudge
    
    return 0.13 * Cmfg * Fcert * Fcomp

def materialCost(airplane):
    Waf = 0.065* convert(airplane.emptyWeight, "N", "lb")    # need to change once compnenet weight build-up is complete
    Vh = convert(airplane.speed, "m/s", "kts")  #needs to be max level airspeed, change later
    N = plannedAircraft
    CPI = inflation2012to2019
    Fcert = certFudge
    Fcf = flapFudge
    Fpress = pressFudge

    return 24.896 * (Waf**0.689) * (Vh**0.624) * (N**0.762) * CPI * Fcert * Fcf * Fpress
    
def engineCost(airplane):
    Npp = numberICEngines
    CPI = inflation2012to2019
    Pbhp = convert(airplane.engine.maxPower, "W", "hp")
    
    return 174 * Npp * Pbhp * CPI
    
def propellerCost(airplane):
    Npp = numberICEngines
    CPI = inflation2012to2019
        
    return 3145 * Npp * CPI     # For fixed pitch propeller
    
def powerplantCost(airplane):
    Cengine = engineCost(airplane)
    Cpropeller = propellerCost(airplane)
    
    return Cengine + Cpropeller
    
def avionicsCost(airplane):
    unit = avionicPrice
    CPI = inflation2012to2019
    
    return unit * CPI
    
def landingGearCost(airplane):
    dC = -7500 if retractableGear is False else 0
    CPI = inflation2012to2019
    
    return dC * CPI
    
def fixedCost(airplane):
    Ceng = engineeringCost(airplane)
    Cdev = developmentalSupportCost(airplane)
    Cft = flightTestCost(airplane)
    Ctool = toolingCost(airplane)
    
    return Ceng + Cdev + Cft + Ctool

def variableCost(airplane):
    Cmfg = manufacturingCost(airplane)
    Cqc = qualityControlCost(airplane)
    Cmat = materialCost(airplane)
    Clg = landingGearCost(airplane)
    Cav = avionicsCost(airplane)
    Cpp = powerplantCost(airplane)
    
    return Cmfg + Cqc + Cmat + Clg + Cav + Cpp

################################################################################
# OPERATING COST FUNCTIONS
################################################################################

def maintenanceToFlightHoursRatio(airplane):
    F1 = maintF
    F2 = engineF
    F3 = 0 if retractableGear is False else 0.02
    F4 = VFRF
    F5 = 0 if IFRflight is False else 0.04
    F6 = fuelF
    F7 = flapF
    F8 = certF
    
    return 0.30 + F1 + F2 + F3 + F4 + F5 + F6 + F7 + F8
    
def maintenanceCost(airplane):
    Fmf = maintenanceToFlightHoursRatio(airplane)
    Rap = APmechRate
    Qflgt = flightHoursYear
    CPI = inflation2012to2019
    
    return Fmf * Rap * Qflgt * CPI
    
def storageCost(airplane):
    Rstor = monthlyStorageRate
    CPI = inflation2012to2019
    
    return 12 * Rstor * CPI
    
def annualFuelCost(airplane):
    FFcruise = fuelFlowCruise  # need this 
    Qflgt = flightHoursYear
    Rfuel = fuelRate
    
    return FFcruise * Qflgt * Rfuel
    
def crewCost(airplane):
    Ncrew = airplane.pilots
    Rcrew = pilotRate
    Qflgt = flightHoursYear
    CPI = inflation2012to2019
    
    return Ncrew * Rcrew * Qflgt * CPI
    
def annualInsuranceCost(airplane): #not a super accurate estimation
    Cac = purchasePrice
    CPI = inflation2012to2019
    
    return (500 * CPI) + (0.015 * Cac)
    
def annualEngineOverhaul(airplane):
    Npp = numberICEngines
    Qflgt = flightHoursYear
    CPI = inflation2012to2019
    
    return 5 * Npp * Qflgt * CPI
    
def annualLoanPayment(airplane):
    # P = principalLoan
    # i = interestRate
    # n = payPeriods
    #
    # return (12 * P * i) / (1 - (1/(1+i)**n))
    return 0
    
def totalAnnualCost(airplane):
    Cap = maintenanceCost(airplane)
    Cstor = storageCost(airplane)
    Cfuel = annualFuelCost(airplane)
    Cins = annualInsuranceCost(airplane)
    Cinsp = inspectionCost
    Cover = annualEngineOverhaul(airplane)
    Cloan = annualLoanPayment(airplane)
    
    return Cap + Cstor + Cfuel + Cins + Cinsp + Cover + Cloan
    
def costPerFlightHour(airplane):
    Cyear = totalAnnualCost(airplane)
    Qflgt = flightHoursYear
    
    return = Cyear / Qflgt


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
