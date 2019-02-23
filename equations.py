from convert import *
from parameters import *
from definitions import *

def TakeoffWeight(Airplane, Missions):
    Wpay = PayloadWeight(Mission)
    We = EmptyWeight(Airplane, Mission)
    Wf = FuelWeight(Airplane, Mission)
    
    return Wpay + We + Wf

def PayloadWeight(Mission):
    Wpax = heavyPassengerWeight if Mission.passengers <= 3 else lightPassengerWeight
    Wbag = heavyPassengerBagWeight if Mission.passengers <= 3 else lightPassengerBagWeight
    
    return (Wpax + Wbag) * Mission.passengers + pilotWeight * Mission.pilots

def EmptyWeight(Airplane, Mission):
    W0 = Airplane.takeoffWeight
    
    return 0.759*convert(W0, "N", "lb")**(-0.0164)

def FuelWeight(Airplane, Mission):
    Wi1Wis = [MissionSegmentWeightFraction(Airplane, Mission, segment) for segment in Mission.segments]
    W0 = Airplane.takeoffWeight
    Wbat = BatteryWeight(Airplane)
    
    return W0 * (1.01) * (1 - sum(1/Wi1Wis)) + Wbat

def MissionSegmentWeightFraction(Airplane, Mission, missionSegment):
    Wi1Wis = [Mission.segment[segment].get("weightFraction") for segment in Mission.segments]
    Wi1Wis[Mission.segments.index("cruise")] = CruiseWeightFraction(Airplane, Mission)
    Wi1Wis[Mission.segments.index("loiter")] = LoiterWeightFraction(Airplane, Mission)
    
    return Wi1Wis

def BatteryWeight(Airplane):
    C = BatteryCapacity(Airplane)
    Esb = 265 # Wh/kg
    
    return C / Esb
    
def BatteryCapacity(Airplane):
    Pm = Airplane.power
    t = None # TODO get this info from mission segments
    etaE = MotorEfficiency(Airplane) * CircuitEfficiency()
    
    return Pm * t / etaE
    
def MotorEfficiency(Airplane):
    pass
    
def CircuitEfficiency():
    return 0.98

def Endurance(Airplane, Mission):
    R = Range(Mission, Airplane)
    V = Velocity(Mission, Airplane)
    
    return R/V

def Range(Airplane, Mission, missionSegment):
    etap = Airplane.etap
    Cbhp = Airplane.Cbhp
    wiwi1 = WeightFraction(Mission, Airplane, missionSegment)

    R = (etap / cbhp) * (L/D) * log(wiwi1)

def WeightFraction(Airplane, Mission, missionSegment):
    pass

def PropellerEfficiency(Airplane):
    thrust = Airplane.thrust
    power = Airplane.power
    velocity = Airplane.velocity
    
    etap = (thrust / power) * Velocity
    
    return etap

def CoefficientOfThrust(Airplane, Mission):
    # thrust = Airplane.thrust
    # rho = densityAtAltitude
    # n = Airplane.propellerRotationSpeed
    # D = Airplane.propellerDiameter
    #
    # CT = thrust / (rho * n^2 * D^4)
    #
    # return CT
    return 0.8

def CoefficientOfPower(Airplane):
    power = Airplane.power
    rho = densityAtAltitude
    n = Airplane.propellerRotationSpeed
    D = Airplane.propellerDiameter
    
    CP = power / (rho * n^3 * D^5)
    
    return CP

def CruiseWeightFraction(Airplane, Mission):
    E =
    V =
    Cbhp = Airplane.Cbhp
    etap = Airplane.etap
    LD = Airplane.LDcruise
    
    return exp(-(E * V * Cbhp) / (etap * LD))

def LoiterWeightFraction(Airplane, Mission):
    E =
    V =
    Cbhp = Airplane.Cbhp
    etap = Airplane.etap
    LD = Airplane.LDloiter
    
    return exp(-(E * V * Cbhp) / (etap * LD))

def TakeoffWeight(Airplane, Mission):
    pass

def LandingDistance(Airplane, Mission):
    sL = GroundRollDistance(Airplane, Mission, missionSegment)
    sa = LandingObstacleClearanceDistance(Airplane, Mission)
    
    return sL + sa

def LandingObstacleClearanceDistance(Airplane, Mission):
    return convert(600, "ft", "m")

def GroundRollDistance(Airplane, Mission, missionSegment):
    bfr = DryRunwayBrakingFactor()
    sigma = AtmosphericDensityRatio(Mission, missionSegment)
    WS = WingLoading(Airplane)
    sigma = AtmosphericDensityRatio(Mission, missionSegment)
    CLmax = CoefficientOfLift(Airplane)
    
    sL = brf * WS * (sigma * CLmax)^-1
    
    return sL

def WingLoading(Airplane, Mission, missionSegment):
    S = Airplane.wingPlanform
    W =

def DryRunwayBrakingFactor():
    return convert(80, "ft^3/lb", "m^3/N")

def AtmosphericDensityRatio(Mission, missionSegment):
    altitude = Mission.segment[missionSegment]["altitude"] # TODO: make this safe
    rho = densityAtAltitude(altitude)
    rhoSL = densityAtAltitude(0)
    
    # TODO: finish
    
def TakeoffDistance(Airplane, Mission):
    sLO = LiftoffDistance(Airplane, Mission, missionSegment)
    sOver = TakeoffObstacleClearanceDistance(Airplane, Mission)
    
    return sLO + sOver
    
