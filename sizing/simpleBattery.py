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

# AIRPLANE PARAMETERS
Esb = convert(265, "kWh/kg", "J/kg") # battery specific energy

# MISSION PARAMETERS
MissionWeightFraction = 1 # weight fraction for entire mission
Wpay = convert(800, "lb", "N") # payload weight
#R = convert(300, "nmi", "m") # range
Eloiter = convert(3/4, "hr", "s") # loiter time
Vcruise = convert(183, "kts", "m/s") # cruise speed
Vloiter = convert(120, "kts", "m/s") # speed during loiter
R = convert(300, "nmi", "m") # range

# ASSUMED PARAMETERS
ηpcruise = 0.9 # cruise propeller efficiency
ηploiter = 0.9 # loiter propeller efficiency
ηe = 0.95 # electrical system efficiency
Cbhpcruise = convert(0.4, "lb/hr*hp", "kg/J") # Brake specific fuel consumption during cruise
Cbhploiter = convert(0.5, "lb/hr*hp", "kg/J") # Brake specific fuel consumption during loiter
KLD = 11
Awetted = 1.6

def EmptyWeightFraction(W0): # Empty Weight Fraction
    return 0.759*convert(W0, "N", "lb")**(-0.0164) # 4th trendline

################################################################################
# SIZING
################################################################################

LDmax = KLD * sqrt(Awetted)
Ecruise = R / Vcruise # cruise time

W0 = 10000000
W0guess = convert(2300, "lb", "N")
iteration = 0
while 1 < abs(W0 - W0guess) and iteration < 1000:
    #print("W0guess = {0:.0f}".format(convert(W0guess, "N", "lb")))
    W0 = W0guess
    
    Dcruise = W0guess / LDmax # drag in cruise
    Dloiter = W0guess / LDmax # drag in loiter
    Prcruise = Dcruise*Vcruise / ηpcruise # power required
    Prloiter = Dloiter*Vloiter / ηploiter # power required
    
    cbcruise = Prcruise*Ecruise / ηe # battery capacity for cruise
    cbloiter = Prloiter*Eloiter / ηe # battery capacity for loiter
    mb = (cbcruise + cbloiter) / Esb # mass of battery
    Wf = mb * 9.80665 # mission fuel weight
    
    We = EmptyWeightFraction(W0) * W0guess
    
    W0guess = We + Wf + Wpay # gross weight
    
    iteration += 1
W0 = W0guess

if iteration >= 1000:
    print("WARNING: iteration cap reached")

################################################################################
# OUTPUT
################################################################################

print("We = {0:4.0f} lb".format(convert(We, "N", "lb")))
print("Wf = {0:4.0f} lb ({1:.0f} kWh)".format(convert(Wf, "N", "lb"), convert(cbcruise + cbloiter, "J", "kWh")))
print("W0 = {0:4.0f} lb".format(convert(W0, "N", "lb")))