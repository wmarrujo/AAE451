# PATHS

import sys
import os
hereDirectory = os.path.dirname(os.path.abspath(__file__))
rootDirectory = hereDirectory

# LOCAL DEPENDENCIES

from utilities import *
from sizing import *

# EXTERNAL DEPENDENCIES

from matplotlib.pyplot import *
from scipy.optimize import curve_fit
from copy import copy

################################################################################
# RELATIONSHIPS
################################################################################

def fit_func(xs, a, b):
    return [exponentialForm(x, a, b) for x in xs]

def exponentialForm(x, a, b):
    return a * exp(b * x)

def invExponentialForm(y, a, b):
    return log(y / a) / b
    
################################################################################
# DEFINITIONS
################################################################################

# SIZING MATRIX CENTER

WS = convert(20, "lb/ft^2", "N/m^2")
PW = convert(0.072, "hp/lb", "W/N")

# DRIVNG PARAMETERS MATRIX

WSs = [WS*0.8, WS, WS*1.2]
PWs = [PW*0.9, PW, PW*1.1]

DPs = [[{
    "wing loading": WS,
    "power to weight ratio": PW
    } for WS in WSs] for PW in PWs]

# Driving Parameters (used for fit curves)
fit_WS = linspace(WS*0.7, WS*1.3, 1000)
fit_PW = linspace(PW*0.7, PW*1.3, 1000)

# AIRPLANE

airplaneName = "Gopher"

# GET DRIVING PARAMETERS

data = map2D(lambda DP: getAirplaneDesignData(airplaneName, DP, designMission), DPs) # FIXME: should this be reference mission data?
p = map2D(lambda d: getPerformanceParameters(d["initial airplane"], d["simulation"], d["final airplane"]), data)

# make matrix for each driving parameter independently

pWS = [[convert(WS, "N/m^2", "lb/ft^2") for WS in copy(WSs)] for PW in PWs]
pPW = transpose([[convert(PW, "W/N", "hp/lb") for PW in copy(PWs)] for WS in WSs])
fWS = [convert(WS, "N/m^2", "lb/ft^2") for WS in fit_WS]
fPW = [convert(PW, "W/N", "hp/lb") for PW in fit_PW]

# make matrix for each performance parameter independently

pC = [[True for PP in row] for row in p] # TODO: cache convergence # Verification that simulation converged at this value
pWe = [[convert(PP["empty weight"], "N", "lb") for PP in row] for row in p]
pdT0 = [[convert(PP["takeoff field length"], "m", "ft") for PP in row] for row in p]
pdL = [[convert(PP["landing field length"], "m", "ft") for PP in row] for row in p]
pR = [[convert(PP["range"], "m", "nmi") for PP in row] for row in p]
pV = [[convert(PP["average ground speed"], "m/s", "kts") for PP in row] for row in p]
pT = [[convert(PP["flight time"], "s", "hr") for PP in row] for row in p]
pF = [[convert(PP["fuel used"], "N", "lb") for PP in row] for row in p]

constrainedFieldLength = convert(minimumTakeoffFieldLength, "m", "ft")

################################################################################
# GROSS WEIGHT TRENDS
################################################################################

W0params = []

figure()
for (Cs, WSs, Wes) in zip(pC, pWS, pWe): # for each row
    # Clean list by checking if solution converged
    cleanWSs = dropOnOtherList(WSs, Cs)
    cleanWes = dropOnOtherList(Wes, Cs)
    W0param, pconv = curve_fit(fit_func, cleanWSs, cleanWes, p0=(1, 0))
    a, b = (W0param[0], W0param[1])

    W0params.append([a,b])

    plot(cleanWSs, cleanWes, "k.")
    plot(fWS, [exponentialForm(WS, a, b) for WS in fWS])

title("Empty Weight Trends")
xlabel("Wing Loading [lb/ft^2]")
ylabel("Empty Weight [lb]")

################################################################################
# TAKEOFF DISTANCE CROSS PLOT
################################################################################
W0fromdT0Intersection = []

figure()

for row, (Cs, WSs, dT0s) in enumerate(zip(pC, pWS, pdT0)):
    cleanWSs = dropOnOtherList(WSs, Cs)
    cleandT0s = dropOnOtherList(dT0s, Cs)
    plot(cleanWSs, cleandT0s, "k.")

    # Create fit curves
    params, pconv = curve_fit(fit_func, cleanWSs, cleandT0s, p0=(1, 0))
    plot(fWS, [exponentialForm(WS, params[0], params[1]) for WS in fWS])

     # Find intersection of curve with flight time limit
    WS_dT0Intersection = invExponentialForm(constrainedFieldLength, params[0], params[1])
    W0_WS_dT0Intersection = invExponentialForm(WS_dT0Intersection, W0params[row][0], W0params[row][1])
    W0fromdT0Intersection.append(W0_WS_dT0Intersection)

hlines(constrainedFieldLength, fWS[0], fWS[-1], colors = "k")

title("Takeoff Distance")
xlabel("Wing Loading [lb/ft^2]")
ylabel("Takeoff Field Length [ft]")

################################################################################
# LANDING DISTANCE CROSS PLOT
################################################################################
W0fromdLIntersection = []

figure()

for row, (Cs, WSs, dLs) in enumerate(zip(pC, pWS, pdL)):
    cleanWSs = dropOnOtherList(WSs, Cs)
    cleandLs = dropOnOtherList(dLs, Cs)
    plot(cleanWSs, cleandLs, "k.")

    # Create fit curves
    params, pconv = curve_fit(fit_func, cleanWSs, cleandLs, p0=(1, 0))
    plot(fWS, [exponentialForm(WS, params[0], params[1]) for WS in fWS])

     # Find intersection of curve with flight time limit
    W0_dLIntersection = invExponentialForm(constrainedFieldLength, params[0], params[1])
    W0_WS_dLIntersection = invExponentialForm(W0_dLIntersection, W0params[row][0], W0params[row][1])
    W0fromdLIntersection.append(W0_WS_dLIntersection)

    print(W0fromdLIntersection)

hlines(constrainedFieldLength, fWS[0], fWS[-1], colors = "k")

title("Landing Distance")
xlabel("Wing Loading [lb/ft^2]")
ylabel("Landing Field Length [ft]")

################################################################################
# SIZING PLOT
################################################################################

###### SIZING PLOT
# Plot wing loading vs. empty weight grid
offset = 4 #lb/ft^2

figure()
for row, (Cs, WSs, Wes) in enumerate(zip(pC, pWS, pWe)): # for each row
    # Clean list by checking if solution converged
    cleanWSs = dropOnOtherList(WSs, Cs)
    cleanWes = dropOnOtherList(Wes, Cs)

    plot(cleanWes, cleanWSs, "k")

for (Cs, WSs, Wes) in zip(transpose(pC), transpose(pWS), transpose(pWe)): # for each row
    # Clean list by checking if solution converged
    cleanWSs = dropOnOtherList(WSs, Cs)
    cleanWes = dropOnOtherList(Wes, Cs)

    plot(cleanWes, cleanWSs, "k")

title("Carpet Plot")
xlabel("Wing Loading")
ylabel("Empty Weight")

################################################################################

show()
