from convert import *
from parameters import *
from definitions import *

def PayloadWeight(Mission):
    Wpax = heavyPassengerWeight if Mission.passengers <= 3 else lightPassengerWeight
    Wbag = heavyPassengerBagWeight if Mission.passengers <= 3 else lightPassengerBagWeight
    
    return (Wpax + Wbag) * Mission.passengers + pilotWeight * Mission.pilots

def Endurance(Mission, Airplane):
    R = Range(Mission, Airplane)
    V = Velocity(Mission, Airplane)
    
    return R/V

def Range(Mission, Airplane, missionSegment):
    etap = Airplane.etap
    Cbhp = Airplane.Cbhp
    wiwi1 = WeightFraction(Mission, Airplane, missionSegment)

    R = (etap / cbhp) * (L/D) * log(wiwi1)

def WeightFraction(Mission, Airplane, missionSegment):
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

def FuelWeight(Airplane, Mission):
    WiWi1s = [Mission.segment[segment]["weightFraction"] for segment in Mission.segments]
    # TODO: finish
    # TODO: replace cruise & loiter segments with actual values
    # TODO: make safe so it doesn't crash when the weightFraction is undefined for cruise & loiter

def LandingDistance(Airplane, Mission):
    sL = Airplane.groundRoll
    sa = LandingObstacleClearanceDistance(Airplane, Mission)
    
    return (sL + sa)

def LandingObstacleClearanceDistance(Airplane, Mission):
    return convert(600, "ft", "m")

def GroundRollDistance(Airplane, Mission, missionSegment):
    bfr = DryRunwayBrakingFactor()
    sigma = AtmosphericDensityRatio(Mission, missionSegment)
    WS = WingLoading(Airplane)

def WingLoading(Airplane):
    pass

def DryRunwayBrakingFactor():
    return convert(80, "ft^3/lb", "m^3/N")

def AtmosphericDensityRatio(Mission, missionSegment):
    altitude = Mission.segment[missionSegment]["altitude"] # TODO: make this safe
    rho = densityAtAltitude(altitude)
    rhoSL = densityAtAltitude(0)
    
    


