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
fit_WS = linspace(WS*0.5, WS*1.5, 1000)
fit_PW = linspace(PW*0.5, PW*1.5, 1000)

# AIRPLANE

airplaneName = "Gopher"

# GET DRIVING PARAMETERS

data = map2D(lambda DP: getAirplaneDesignData(airplaneName, DP, designMission), DPs) # FIXME: should this be reference mission data?
p = map2D(lambda d: getPerformanceParameters(d["initial airplane"], d["simulation"], d["final airplane"]), data)

# make matrix for each driving parameter independently

pWS = map2D(lambda DP: convert(DP["wing loading"], "N/m^2", "lb/ft^2"), DPs)
pPW = transpose(map2D(lambda DP: convert(DP["power to weight ratio"], "W/N", "hp/lb"), DPs))
fWS = [convert(WS, "N/m^2", "lb/ft^2") for WS in fit_WS]
fPW = [convert(PW, "W/N", "hp/lb") for PW in fit_PW]

# make matrix for each performance parameter independently

pC = [[True for PP in row] for row in p] # TODO: cache convergence # Verification that simulation converged at this value
pWe = map2D(lambda PP: convert(PP["empty weight"], "N", "lb"), p)
pdT0 = map2D(lambda PP: convert(PP["takeoff field length"], "m", "ft"), p)
pdL = map2D(lambda PP: convert(PP["landing field length"], "m", "ft"), p)
pR = map2D(lambda PP: convert(PP["range"], "m", "nmi"), p)
pT = map2D(lambda PP: convert(PP["mission time"], "s", "hr"), p)

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

     # Find intersection of curve with field length limit
    WS_dT0Intersection = invExponentialForm(constrainedFieldLength, params[0], params[1])
    W0_WS_dT0Intersection = exponentialForm(WS_dT0Intersection, W0params[row][0], W0params[row][1])
    W0fromdT0Intersection.append(W0_WS_dT0Intersection)

hlines(constrainedFieldLength, fWS[0], fWS[-1], colors = "k")

title("Takeoff Distance")
xlabel("Wing Loading [lb/ft^2]")
ylabel("Takeoff Field Length [ft]")

################################################################################
# MISSION TIME CROSS PLOT
################################################################################
W0fromTIntersection = []

figure()

for row, (Cs, WSs, Ts) in enumerate(zip(pC, pWS, pT)):
    cleanWSs = dropOnOtherList(WSs, Cs)
    cleanTs = dropOnOtherList(Ts, Cs)
    plot(cleanWSs, cleanTs, "k.")

    # Create fit curves
    params, pconv = curve_fit(fit_func, cleanWSs, cleanTs, p0=(1, 0))
    plot(fWS, [exponentialForm(WS, params[0], params[1]) for WS in fWS])

     # Find intersection of curve with flight time limit
    WS_TIntersection = invExponentialForm(convert(maximumFlightTime, "s", "hr"), params[0], params[1])
    W0_WS_TIntersection = exponentialForm(WS_TIntersection, W0params[row][0], W0params[row][1])
    W0fromTIntersection.append(W0_WS_TIntersection)

hlines(convert(maximumFlightTime, "s", "hr"), fWS[0], fWS[-1], colors = "k")

title("Flight Time")
xlabel("Wing Loading [lb/ft^2]")
ylabel("Flight Time [hr]")

################################################################################
# SIZING PLOT
################################################################################
###### SIZING PLOT
# Plot wing loading vs. empty weight grid
offset = 4 #lb/ft^2

figure()
# P/W Contour
for row, (Cs, WSs, Wes) in enumerate(zip(pC, pWS, pWe)): # for each row
    # Clean list by checking if solution converged
    cleanOffsetWSs = [WS+offset*row for WS in dropOnOtherList(WSs, Cs)]
    cleanWes = dropOnOtherList(Wes, Cs)
    plot(cleanOffsetWSs, cleanWes, "k")

# W/S Contour
for row, (Cs, WSs, Wes) in enumerate(zip(transpose(pC), pWS, transpose(pWe))): # for each row
    
    # Clean list by checking if solution converged
    cleanOffsetWSs = [WS+offset*row for WS in dropOnOtherList(WSs, Cs)]
    cleanWes = dropOnOtherList(Wes, Cs)
    plot(cleanOffsetWSs, cleanWes, "k")
    
# dT0 Intersection Curve
cleanOffsetWSs = [WS for WS in dropOnOtherList(WSs, Cs)]
params, pconv = curve_fit(fit_func, cleanOffsetWSs, W0fromdT0Intersection, p0=(1, 0))
plot(fWS, [exponentialForm(WS, params[0], params[1]) for WS in fWS])

# T Intersection Curve
cleanOffsetWSs = [WS for WS in dropOnOtherList(WSs, Cs)]
params, pconv = curve_fit(fit_func, cleanOffsetWSs, W0fromTIntersection, p0=(1, 0))
plot(fWS, [exponentialForm(WS, params[0], params[1]) for WS in fWS])

title("Carpet Plot")
xlabel("Wing Loading")
ylabel("Empty Weight")

################################################################################

show()
