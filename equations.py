from convert import *
from parameters import *
from definitions import *
from stdatmo import *

from functools import reduce
product = lambda L: reduce((lambda x, y: x * y), L)

################################################################################

def TakeoffWeight(Airplane, Mission):
    Wpay = PayloadWeight(Mission)
    We = EmptyWeight(Airplane, Mission)
    Wf = FuelWeight(Airplane, Mission)
    print("Payload Weight = ", convert(Wpay,"N","lb"))
    print("Empty Weight = ", convert(We,"N","lb"))
    print("Fuel Weight = ", convert(Wf,"N","lb"))
    
    return Wpay + We + Wf

def PayloadWeight(Mission):
    Wpax = heavyPassengerWeight if Mission.passengers <= 3 else lightPassengerWeight
    Wbag = heavyPassengerBagWeight if Mission.passengers <= 3 else lightPassengerBagWeight
    pax = Mission.passengers
    pilots = Mission.pilots
    
    return (Wpax + Wbag) * pax + pilotWeight * pilots

def EmptyWeight(Airplane, Mission):
    W0 = Airplane.takeoffWeight
    
    return W0 * 1.57 * (W0)**-0.1 # from some historical data for twin engine
    # return 0.759*convert(W0, "N", "lb")**(-0.0164) # correlation for single engine

def FuelWeight(Airplane, Mission):
    Wi1Wis = [MissionSegmentWeightFraction(Airplane, Mission, segment) for segment in Mission.segments]
    W0 = Airplane.takeoffWeight
    #print("WFractions = ", list(zip(Mission.segments, Wi1Wis)))
    
    return W0 * (1 - product(Wi1Wis))

def MissionSegmentInitialWeight(Airplane, Mission, missionSegment):
    W0 = Airplane.takeoffWeight
    Wi1Wis = [1]
    Wis = [W0]
    for segment in Mission.segments:
        Wf = MissionSegmentFuelWeightUsed(Airplane, Mission, segment)
        Wi = Wis[-1]
        Wis.append(Wi - Wf)
        Wi1 = Wis[-1]
        Wi1Wis.append(Wi1/Wi)
    Wi1Wis = Wi1Wis[0:Mission.segments.index(missionSegment)+1] # filter to before missionSegment
    
    return W0*product(Wi1Wis)

def MissionSegmentFinalWeight(Airplane, Mission, missionSegment):
    Wi = MissionSegmentInitialWeight(Airplane, Mission, missionSegment)
    Wf = MissionSegmentFuelWeightUsed(Airplane, Mission, missionSegment)
    print(missionSegment)
    print( convert(Wf, "N" , "lb" ) )
    return Wi - Wf

def MissionSegmentWeightFraction(Airplane, Mission, missionSegment):
    Wi = MissionSegmentInitialWeight(Airplane, Mission, missionSegment)
    Wi1 = MissionSegmentFinalWeight(Airplane, Mission, missionSegment)
    
    return Wi1/Wi

def MissionSegmentFuelWeightUsed(Airplane, Mission, missionSegment): # asks powerplant how much fuel weight was used for a certain mission segment (N)
    energyUsed = MissionSegmentEnergyUsed(Airplane, Mission, missionSegment)
    altitude = Mission.segment[missionSegment]["altitude"]
    rho = densityAtAltitude(altitude)
    rhoSL = densityAtAltitude(0)
    lapseRate = (rho/rhoSL)**engineLapseRateCoefficient
    print(missionSegment)
    print(energyUsed)
    energyNeeded = energyUsed / (0.25 * lapseRate) # FIXME: need to incorporate the engine ineffeciency
    p = Airplane.powerplant.percentEnergyFromBattery
    
    #print("segment: {0:12}, Energy = {1}".format(missionSegment, convert(energyUsed, "J", "MJ"))) # TODO: will need to return to this after drag implementation
    #print(missionSegment)
    #print("Fuel Consumption Rate = {0:0f} L/hr".format(convert( (energyNeeded*(p/batteryEnergyDensity + (1-p)/avgasEnergyDensity))/avgasDensity/Mission.segment[missionSegment]["timeElapsed"], "L/s", "L/hr")))
    return energyNeeded*(p/batteryEnergyDensity + (1-p)/avgasEnergyDensity) * g

def MissionSegmentEnergyUsed(Airplane, Mission, missionSegment):
    segmentTime = Mission.segment[missionSegment]["timeElapsed"]
    segmentPower = MissionSegmentPower(Airplane, Mission, missionSegment)

    return segmentPower * segmentTime

def MissionSegmentPower(Airplane, Mission, missionSegment):
    PSLW0 = Airplane.maxPowerToWeight
    W0 = Airplane.takeoffWeight
    powerPercent = Mission.segment[missionSegment]["powerPercent"]

    #print("Power = {0:0f} hp".format(convert((PSLW0*W0*powerPercent)*lapseRate, "W", "hp")))
    return (PSLW0*W0*powerPercent)

def ParasiteDrag(Airplane, Mission, missionSegment):
    altitude = Mission.segment[missionSegment]["altitude"] # FIXME: bad stopgap measure for now, do proper simulation later
    rho = densityAtAltitude(altitude)
    V = Mission.segment[missionSegment]["speed"] # FIXME: BAD stopgap measure for now, do proper simulation later
    mu = dynamicViscosityAtAltitude(altitude)
    Sref = WingPlanformArea(Airplane)
    CD0miscFactor = Airplane.miscellaneousParasiteDragFactor
    
    def componentDragContribution(component):
        FFi = component.formFactor
        Qi = component.interferenceFactor
        Cfi = component.skinFrictionCoefficient(rho, V, mu)
        Sweti = component.wettedArea
        
        return FFi * Qi * Cfi * Sweti / Sref
    
    CD0Prediction = sum([componentDragContribution(component) for component in Airplane.components])
    
    return CD0Prediction * (1+CD0miscFactor)

def WingPlanformArea(Airplane):
    W0 = Airplane.takeoffWeight
    W0S = Airplane.wingLoading
    
    return W0 / W0S

# def BatteryCapacity(Airplane):
#     Pm = Airplane.power
#     t = None # TODO get this info from mission segments
#     etaE = ElectricMotorEfficiency(Airplane) * CircuitEfficiency()
#
#     return Pm * t / etaE
#
# def ElectricMotorEfficiency(Airplane):
#     return 0.9
#
# def CircuitEfficiency():
#     return 0.98

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
    