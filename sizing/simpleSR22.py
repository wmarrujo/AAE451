import sys
sys.path.append("..")
from convert import convert # unit conversions
from stdatmo import * # standard atmospheric conditions
from scipy import * # math
from matplotlib.pyplot import * # plotting

################################################################################
# INITIAL PARAMETERS
################################################################################

# CONSTANTS
gasWeight = convert(6, "lb/gal", "N/m^3") # weight per gallon of gas

# AIRCRAFT PARAMETERS
PSL = convert(310, "hp", "W") # power at sea level
TOlength = convert(1868, "ft", "m") # takeoff runway length
LLength = convert(2345, "ft", "m") # landing runway length
R = convert(700, "nmi", "m") # range at 8000ft 
b = convert(38 + 1/3, "ft", "m") # wingspan
S = convert(149.9, "ft^2", "m^2") # wing planform area
We = convert(2253, "lb", "N") # empty weight
W0 = convert(3600, "lb", "N") # gross weight
AR = 9.8 # aspect ratio
n = 2700*2*pi # cruise RPM
seats = 5 # seats (including pilot)
fuelCapacity = convert(92, "gal", "m^3") # fuel capacity
fuelBurn = convert(18.6, "gal/hr", "m^3/s") # fuel burn rate at cruise

# MISSION PARAMETERS
WeightFraction01 = 0.99 # taxi & takeoff
WeightFraction12 = 0.985 # climb
WeightFraction34 = 0.995 # descent & approach
WeightFraction45 = 0.99 # climb to loiter
WeightFraction78 = 0.995 # landing & taxi
Wpay = convert(800, "lb", "N") # payload weight
#R = convert(300, "nmi", "m") # range
Eloiter = convert(3/4, "hr", "s") # loiter time
Vcruise = convert(183, "kts", "m/s") # cruise speed
Vloiter = convert(120, "kts", "m/s") # speed during loiter

# ASSUMED PARAMETERS
etapcruise = 0.9 # cruise propeller efficiency
etaploiter = 0.9 # loiter propeller efficiency
Cbhpcruise = convert(0.4, "lb/hr*hp", "kg/J") # Brake specific fuel consumption during cruise
Cbhploiter = convert(0.5, "lb/hr*hp", "kg/J") # Brake specific fuel consumption during loiter
CD0 = 0.02 # Parasite Drag Coefficient
e = 0.8 # oswald efficiency factor
KLD = 11
Awetted = 1.6

def EmptyWeightFraction(W0): # Empty Weight Fraction
    #return 1.51e-5 * convert(W0, "N", "lb") + 0.637 # trendline from composite airplanes from airplane database
    #return 1.51*convert(W0, "N", "lb")**(-1) # raymer
    #return 0.911*convert(W0, "N", "lb")**(-0.053) # nicolai
    #return 0.688*convert(W0, "N", "lb")**(-9.23e-3) # 2nd trendline
    #return 1.69*convert(W0, "N", "lb")**(-0.124) # 3rd trendline
    return 0.759*convert(W0, "N", "lb")**(-0.0164) # 4th trendline

################################################################################
# SIZING
################################################################################

# LDmax = 1/2 * 1/sqrt(CD0 / (pi * AR * e)) # maximum L/D
LDmax = KLD * sqrt(Awetted)
Ecruise = R / Vcruise # cruise time
print("E = ", convert(Ecruise, "s", "hr"))
WeightFraction23 = exp(-(Ecruise * Vcruise * Cbhpcruise) / (etapcruise * LDmax)) # cruise-climb
WeightFraction67 = exp(-(Eloiter * Vloiter * Cbhploiter) / (etaploiter * LDmax)) # loiter
MissionWeightFraction = WeightFraction01 * WeightFraction12 * WeightFraction23 * WeightFraction34 * WeightFraction45 * WeightFraction67 * WeightFraction78
FuelWeightFraction = 1.01 * (1 - MissionWeightFraction)

W0guess = convert(2300, "lb", "N")
iteration = 0
while 1 < abs(W0 - W0guess) and iteration < 1000:
    #print("W0guess = {0:.0f}".format(convert(W0guess, "N", "lb")))
    W0 = W0guess
    
    We = EmptyWeightFraction(W0) * W0guess
    Wf = W0guess * FuelWeightFraction # mission fuel weight
    W0guess = We + Wf + Wpay # gross weight
    
    iteration += 1
W0 = W0guess

if iteration >= 1000:
    print("WARNING: iteration cap reached")

################################################################################
# OUTPUT
################################################################################

print("We = {0:4.0f} lb".format(convert(We, "N", "lb")))
print("Wf = {0:4.0f} lb ({1:.0f} gal)".format(convert(Wf, "N", "lb"), convert(Wf / gasWeight, "m^3", "gal")))
print("W0 = {0:4.0f} lb".format(convert(W0, "N", "lb")))