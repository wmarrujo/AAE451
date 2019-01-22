from scipy import *

def emptyWeightFraction(emptyWeight, fullWeight):
    return emptyWeight / fullWeight

def aspectRatio(wingspan, chord):
    return wingspan / chord

def wingArea(wingspan, chord):
    return chord * wingspan

def dynamicPressure(density, speed):
    return 0.5 * density * speed**2

def wingLoading(dynamicPressure, liftCoefficient):
    return dynamicPressure * liftCoefficient

def stallSpeed(weight, freestreamDensity, wingArea, maxLiftCoefficient):
    return sqrt((2 * weight) / (freestreamDensity * wingArea * maxLiftCoefficient))

def inducedDragCoefficient(liftCoefficient, oswaldEfficiencyFactor, aspectRatio):
    return liftCoefficient**2 / (pi * oswaldEfficiencyFactor * aspectRatio)

def dragCoefficient(zeroLiftDragCoefficient, inducedDragCoefficient):
    return zeroLiftDragCoefficient + inducedDragCoefficient

def powerRequired(thrustRequired, speed):
    return thrustRequired * speed

# TAKEOFF

def thrustRequiredForLevelFlight(weight, liftOverDrag):
    return weight / liftOverDrag



# CLIMB



# CRUISE



# LANDING

