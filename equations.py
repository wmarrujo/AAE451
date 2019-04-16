from utilities import *

from constants import *
from parameters import *

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
    Tavail = AirplaneThrust(airplane)
    CD0 = ParasiteDragCoefficient(airplane)
    
    def KValue(airplane):
        AR = airplane.aspectRatio
        e = airplane.oswaldEfficiencyFactor
        
        return 1 / (pi * AR * e)
    
    K = KValue(airplane)
    W = AirplaneWeight(airplane)
    rho = densityAtAltitude(airplane.altitude)
    S = airplane.wing.planformArea
    CDmin = 9
    
    
    pass
    

################################################################################
# PRODUCTION COST FUNCTIONS
################################################################################

def EngineeringHours(airplane, plannedAircraft):
    Waf =  0.065* convert(airplane.initialGrossWeight, "N", "lb")   # need to change once compnenet weight build-up is complete
    # Vh = convert(airplane.speed, "m/s", "kts")  #needs to be max level airspeed, change later
    Vh = 185
    N = plannedAircraft
    Fcert = certFudge
    Fcf = flapFudge
    Fcomp = 1 + airplane.compositeFraction
    Fpress = pressFudge
    
    #print("empty weight = {}".format(convert(airplane.initialGrossWeight, "N", "lb")))
    
    return 0.0396 * (Waf**0.791) * (Vh**1.526) * (N**0.183) * Fcert * Fcf * Fcomp * Fpress

def ToolingHours(airplane, plannedAircraft):
    Waf =  0.065* convert(airplane.initialGrossWeight, "N", "lb")    # need to change once compnenet weight build-up is complete
    # Vh = convert(airplane.speed, "m/s", "kts")  #needs to be max level airspeed, change later
    Vh = 185
    N = plannedAircraft
    Qm = plannedAircraft/60
    Ftaper = taperFudge
    Fcf = flapFudge
    Fcomp = 1 + airplane.compositeFraction
    Fpress = pressFudge
    
    return 1.0032 * (Waf**0.764) * (Vh**0.899) * (N**0.178) * (Qm**0.066) * Ftaper * Fcf * Fcomp * Fpress
    
def ManufacturingHours(airplane, plannedAircraft):
    Waf = 0.065* convert(airplane.initialGrossWeight, "N", "lb")
    # Vh = convert(airplane.speed, "m/s", "kts")  #needs to be max level airspeed, change later
    Vh = 185
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
    Waf = 0.065* convert(airplane.initialGrossWeight, "N", "lb")   # need to change once compnenet weight build-up is complete
    # Vh = convert(airplane.speed, "m/s", "kts")  #needs to be max level airspeed, change later
    Vh = 185
    Np = numberFlightTestAircraft
    Fcert = certFudge
    Fcf = flapFudge
    Fcomp = 1 + 0.5*airplane.compositeFraction
    Fpress = pressFudge
    CPI = inflation2012to2019
    
    return 0.06458 * (Waf**0.873) * (Vh**1.89) * (Np**0.346) * Fcert * Fcf * Fcomp * Fpress * CPI
    
def FlightTestCost(airplane):
    Waf = 0.065* convert(EmptyWeight(airplane), "N", "lb")   # need to change once compnenet weight build-up is complete
    # Vh = convert(airplane.speed, "m/s", "kts")  #needs to be max level airspeed, change later
    Vh = 185
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
    Waf = 0.065* convert(airplane.initialGrossWeight, "N", "lb")
    # Vh = convert(airplane.speed, "m/s", "kts")  #needs to be max level airspeed, change later
    Vh = 185
    N = plannedAircraft
    CPI = inflation2012to2019
    Fcert = certFudge
    Fcf = flapFudge
    Fpress = pressFudge

    return (24.896 * (Waf**0.689) * (Vh**0.624) * (N**0.762) * CPI * Fcert * Fcf * Fpress) / N
    
def EngineCost(engines):
    Npp = numberICEngines
    CPI = inflation2012to2019
    
    PSI = [engine.maxPower for engine in engines]
    Pbhp = convert(PSI[0], "W", "hp")
    
    return 174 * Npp * Pbhp * CPI
    
def PropellerCost(airplane):
    Npp = numberICEngines
    CPI = inflation2012to2019
    
    return 3145 * Npp * CPI  # For fixed pitch propeller
    
def PowerplantCost(airplane, engines):
    Cengine = EngineCost(engines)
    Cpropeller = PropellerCost(airplane)
    
    return Cengine + Cpropeller

def LandingGearCost(airplane):
    dC = -7500 if airplane.retractableGear is False else 0
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

def VariableCost(airplane, engines, plannedAircraft):
    #this is a per aircraft cost
    Cmfg = ManufacturingCost(airplane, plannedAircraft)
    Cqc = QualityControlCost(airplane, plannedAircraft)
    Cmat = MaterialCost(airplane, plannedAircraft)
    Clg = LandingGearCost(airplane)
    Cav = avionicPrice
    Cheat = cabinHeaterPrice
    Cseat = SeatingCost(airplane)
    Cmfgins = manufacturerLiabilityInsurance
    Cpp = PowerplantCost(airplane, engines)
    
    return Cmfg + Cqc + Cmat + Clg + Cav + Cheat + Cseat + Cmfgins + Cpp

################################################################################
# OPERATING COST FUNCTIONS
################################################################################

def MaintenanceToFlightHoursRatio(airplane):
    F1 = maintF
    F2 = engineF
    F3 = 0 if airplane.retractableGear is False else 0.02
    F4 = VFRF
    F5 = 0 #if IFRflight is False
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
    
def AnnualFuelCost(airplane):
    FFcruise = fuelFlowCruise  # need this!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    Qflgt = flightHoursYear
    Rfuel = fuelRate
    
    return FFcruise * Qflgt * Rfuel
    
def CrewCost(airplane):
    Ncrew = airplane.pilots
    Rcrew = pilotRate
    Qflgt = flightHoursYear
    CPI = inflation2012to2019
    
    return Ncrew * Rcrew * Qflgt * CPI
    
def AnnualInsuranceCost(airplane): #not a super accurate estimation
    Cac = purchasePrice
    CPI = inflation2012to2019
    
    return (500 * CPI) + (0.015 * Cac)
    
def AnnualEngineOverhaul(airplane):
    Npp = numberICEngines
    Qflgt = flightHoursYear
    CPI = inflation2012to2019
    
    return 5 * Npp * Qflgt * CPI
    
def AnnualLoanPayment(airplane):
    # P = principalLoan
    # i = interestRate
    # n = payPeriods
    #
    # return (12 * P * i) / (1 - (1/(1+i)**n))
    return 0
    
def TotalAnnualCost(airplane):
    Cap = MaintenanceCost(airplane)
    Cstor = StorageCost(airplane)
    Cfuel = AnnualFuelCost(airplane)
    Cins = AnnualInsuranceCost(airplane)
    Cinsp = inspectionCost
    Cover = AnnualEngineOverhaul(airplane)
    Cloan = AnnualLoanPayment(airplane)
    
    return Cap + Cstor + Cfuel + Cins + Cinsp + Cover + Cloan
    
def CostPerFlightHour(airplane):
    Cyear = TotalAnnualCost(airplane)
    Qflgt = flightHoursYear
    
    return Cyear / Qflgt

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
