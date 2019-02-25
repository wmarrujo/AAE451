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
    
    return W0 * (1 - sum(1/Wi1Wis))

def MissionSegmentInitialWeight(Airplane, Mission, missionSegment):
    W0 = Airplane.takeoffWeight
    Wi1Wis = [1]
    for segment in Mission.segments:
        Wf = MissionSegmentFuelWeightUsed(Airplane, Mission, segment)
        Wi1 = Wi1Wi[-1] - Wf
        Wi1Wis += [Wi1/Wi]
    Wi1Wis = Wi1Wis[0:Mission.segments.index(missionSegment)] # filter to before missionSegment
    
    return W0*product(Wi1Wis)

def MissionSegmentFinalWeight(Airplane, Mission, missionSegment):
    Wi = MissionSegmentInitialWeight(Airplane, Mission, missionSegment)
    Wf = MissionSegmentFuelWeightUsed(Airplane, Mission, segment)
    
    return Wi - Wf

def MissionSegmentWeightFraction(Airplane, Mission, missionSegment):
    Wi = MissionSegmentInitialWeight(missionSegment)
    Wi1 = MissionSegmentFinalWeight(missionSegment)
    
    return Wi1/Wi

def MissionSegmentFuelWeightUsed(Airplane, Mission, missionSegment): # asks powerplant how much fuel weight was used for a certain mission segment (N)
    energyUsed = MissionSegmentEnergyUsed(Airplane, Mission, missionSegment)
    
    return Airplane.powerplant.fuelWeightForEnergyUsed(missionSegment, energyUsed)

def MissionSegmentEnergyUsed(Airplane, Mission, missionSegment):
    pass

# SIMULATION

def simulateClimb(initialFlightCondition, Airplane, Mission):
    pass

# UNORGANIZED

# def Endurance(Airplane, Mission):
#     R = Range(Mission, Airplane)
#     V = Velocity(Mission, Airplane)
# 
#     return R/V
# 
# def Range(Airplane, Mission, missionSegment):
#     etap = Airplane.etap
#     Cbhp = Airplane.Cbhp
#     wiwi1 = WeightFraction(Mission, Airplane, missionSegment)
# 
#     R = (etap / cbhp) * (L/D) * log(wiwi1)
# 
# def WeightFraction(Airplane, Mission, missionSegment):
#     pass
# 
# def PropellerEfficiency(Airplane):
#     thrust = Airplane.thrust
#     power = Airplane.power
#     velocity = Airplane.velocity
# 
#     etap = (thrust / power) * Velocity
# 
#     return etap
# 
# def CoefficientOfThrust(Airplane, Mission):
#     # thrust = Airplane.thrust
#     # rho = densityAtAltitude
#     # n = Airplane.propellerRotationSpeed
#     # D = Airplane.propellerDiameter
#     #
#     # CT = thrust / (rho * n^2 * D^4)
#     #
#     # return CT
#     return 0.8
# 
# def CoefficientOfPower(Airplane):
#     power = Airplane.power
#     rho = densityAtAltitude
#     n = Airplane.propellerRotationSpeed
#     D = Airplane.propellerDiameter
# 
#     CP = power / (rho * n^3 * D^5)
# 
#     return CP

# def CruiseWeightFraction(Airplane, Mission):
#     E =
#     V =
#     Cbhp = Airplane.Cbhp
#     etap = Airplane.etap
#     LD = Airplane.LDcruise
# 
#     return exp(-(E * V * Cbhp) / (etap * LD))
# 
# def LoiterWeightFraction(Airplane, Mission):
#     E =
#     V =
#     Cbhp = Airplane.Cbhp
#     etap = Airplane.etap
#     LD = Airplane.LDloiter
# 
#     return exp(-(E * V * Cbhp) / (etap * LD))
# 
# def TakeoffWeight(Airplane, Mission):
#     pass
# 
# def LandingDistance(Airplane, Mission):
#     sL = GroundRollDistance(Airplane, Mission, missionSegment)
#     sa = LandingObstacleClearanceDistance(Airplane, Mission)
# 
#     return sL + sa
# 
# def LandingObstacleClearanceDistance(Airplane, Mission):
#     return convert(600, "ft", "m")
# 
# def GroundRollDistance(Airplane, Mission, missionSegment):
#     bfr = DryRunwayBrakingFactor()
#     sigma = AtmosphericDensityRatio(Mission, missionSegment)
#     WS = WingLoading(Airplane)
#     sigma = AtmosphericDensityRatio(Mission, missionSegment)
#     CLmax = CoefficientOfLift(Airplane)
# 
#     sL = brf * WS * (sigma * CLmax)^-1
# 
#     return sL
# 
# def WingLoading(Airplane, Mission, missionSegment):
#     S = Airplane.wingPlanform
#     W = MissionSegmentWeight(Airplane, Mission, missionSegment)
# 
#     return W / S
# 
# def DryRunwayBrakingFactor():
#     return convert(80, "ft^3/lb", "m^3/N")
# 
# def AtmosphericDensityRatio(Mission, missionSegment):
#     altitude = Mission.segment[missionSegment]["altitude"] # TODO: make this safe
#     rho = densityAtAltitude(altitude)
#     rhoSL = densityAtAltitude(0)
# 
#     # TODO: finish
# 
# def TakeoffDistance(Airplane, Mission):
#     sLO = LiftoffDistance(Airplane, Mission, missionSegment)
#     sOver = TakeoffObstacleClearanceDistance(Airplane, Mission)
# 
#     return sLO + sOver
    
