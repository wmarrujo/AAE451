# PATHS

import sys
import os
hereDirectory = os.path.dirname(os.path.abspath(__file__))
rootDirectory = hereDirectory

# LOCAL DEPENDENCIES

from utilities import *
from sizing import *
from missions import *

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

# WSs = [WS*0.8, WS*0.9, WS, WS*1.1, WS*1.2]
# PWs = [PW*0.9, PW*0.95, PW, PW*1.05, PW*1.1]
WSs = [WS*0.8, WS, WS*1.2]
PWs = [PW*0.9, PW, PW*1.1]

DPs = [[{
    "wing loading": WS,
    "power to weight ratio": PW
    } for WS in WSs] for PW in PWs]

# Driving Parameters (used for fit curves)
fit_WS = linspace(WS*0.8, WS*1.2, 1000)
fit_PW = linspace(PW*0.8, PW*1.2, 1000)

# AIRPLANE

airplaneName = "Gopher"

# GET DRIVING PARAMETERS

designData = map2D(lambda DP: getAirplaneDesignData(airplaneName, DP, designMission), DPs)
#referenceData = map2D(lambda DP: getReferenceMissionData(airplaneName, DP, designMission, referenceMission, referenceMissionName="reference", closeReferenceMissionFunction=closeReferenceMissionByFuelWeightAndRange), DPs)
abortedData = map2D(lambda DP: getReferenceMissionData(airplaneName, DP, designMission, abortedMission, referenceMissionName="aborted"), DPs)
p = map2D(lambda d: getPerformanceParameters(d["initial airplane"], d["simulation"], d["final airplane"]), designData)
#pR = map2D(lambda d: getPerformanceParameters(d["initial airplane"], d["simulation"], d["final airplane"]), referenceData)
pA = map2D(lambda d: getPerformanceParameters(d["initial airplane"], d["simulation"], d["final airplane"]), abortedData)

# make matrix for each driving parameter independently

PWs = [convert(PW, "W/N", "hp/lb") for PW in PWs]
print(PWs)

pWe = map2D(lambda PP: convert(PP["empty weight"], "N", "lb"), p)
pWS = map2D(lambda DP: convert(DP["wing loading"], "N/m^2", "lb/ft^2"), DPs)
pPW = transpose(map2D(lambda DP: convert(DP["power to weight ratio"], "W/N", "hp/lb"), DPs))
fWS = [convert(WS, "N/m^2", "lb/ft^2") for WS in fit_WS]
fPW = [convert(PW, "W/N", "hp/lb") for PW in fit_PW]

# make matrix for each performance parameter independently

pC = [[True for PP in row] for row in p] # TODO: cache convergence # Verification that simulation converged at this value
pdT0 = map2D(lambda PP: convert(PP["takeoff field length"], "m", "ft"), p)
pdL = map2D(lambda PP: convert(PP["landing field length"], "m", "ft"), pA)
pR = map2D(lambda PP: convert(PP["range"], "m", "nmi"), p)
pT = map2D(lambda PP: convert(PP["mission time"], "s", "hr"), p)

constrainedFieldLength = convert(minimumTakeoffFieldLength, "m", "ft")

################################################################################
# GROSS WEIGHT TRENDS
################################################################################

W0params = []

figure()
for row, (Cs, WSs, Wes) in enumerate(zip(pC, pWS, pWe)): # for each row
    # Clean list by checking if solution converged
    cleanWSs = dropOnOtherList(WSs, Cs)
    cleanWes = dropOnOtherList(Wes, Cs)
    W0param, pconv = curve_fit(fit_func, cleanWSs, cleanWes, p0=(1, 0))
    a, b = (W0param[0], W0param[1])

    W0params.append([a,b])

    plot(cleanWSs, cleanWes)
    plot(fWS, [exponentialForm(WS, a, b) for WS in fWS], label="P/W= {:.4f} hp/lb".format(PWs[row]))

title("Empty Weight Trends")
xlabel("Wing Loading [lb/ft^2]")
ylabel("Empty Weight [lb]")
legend()

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
    plot(fWS, [exponentialForm(WS, params[0], params[1]) for WS in fWS], label="P/W= {:.4f} hp/lb".format(PWs[row]))

     # Find intersection of curve with field length limit
    WS_dT0Intersection = invExponentialForm(constrainedFieldLength, params[0], params[1])
    W0_WS_dT0Intersection = exponentialForm(WS_dT0Intersection, W0params[row][0], W0params[row][1])
    W0fromdT0Intersection.append(W0_WS_dT0Intersection)

hlines(constrainedFieldLength, fWS[0], fWS[-1], colors = "k", label="dT0=2500ft")

title("Takeoff Distance")
xlabel("Wing Loading [lb/ft^2]")
ylabel("Takeoff Field Length [ft]")
legend()

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
    plot(fWS, [exponentialForm(WS, params[0], params[1]) for WS in fWS], label="P/W= {:.4f} hp/lb".format(PWs[row]))

     # Find intersection of curve with field length limit
    WS_dLIntersection = invExponentialForm(constrainedFieldLength, params[0], params[1])
    W0_WS_dLIntersection = exponentialForm(WS_dLIntersection, W0params[row][0], W0params[row][1])
    W0fromdLIntersection.append(W0_WS_dLIntersection)

hlines(constrainedFieldLength, fWS[0], fWS[-1], colors = "k", label="dL=2500ft")

title("Landing Distance")
xlabel("Wing Loading [lb/ft^2]")
ylabel("Landing Field Length [ft]")
legend()

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
    plot(fWS, [exponentialForm(WS, params[0], params[1]) for WS in fWS], label="P/W= {:.4f} hp/lb".format(PWs[row]))

     # Find intersection of curve with flight time limit
    WS_TIntersection = invExponentialForm(convert(maximumFlightTime, "s", "hr"), params[0], params[1])
    W0_WS_TIntersection = exponentialForm(WS_TIntersection, W0params[row][0], W0params[row][1])
    W0fromTIntersection.append(W0_WS_TIntersection)

hlines(convert(maximumFlightTime, "s", "hr"), fWS[0], fWS[-1], colors = "k", label="T=1.5hr")

title("Flight Time")
xlabel("Wing Loading [lb/ft^2]")
ylabel("Flight Time [hr]")
legend()

################################################################################
# CARPET PLOT
################################################################################
###### SIZING PLOT
# Plot wing loading vs. empty weight grid
offset = 4 #lb/ft^2

figure()
# P/W Contour
for row, (Cs, WSs, Wes) in enumerate(zip(pC, pWS, pWe)): # for each row
    # Clean list by checking if solution converged
    cleanOffsetWSs = [WS+(offset*row) for WS in dropOnOtherList(WSs, Cs)]
    cleanWes = dropOnOtherList(Wes, Cs)
    plot(cleanOffsetWSs, cleanWes, "k")

# W/S Contour
for row, (Cs, WSs, Wes) in enumerate(zip(transpose(pC), pWS, transpose(pWe))): # for each row
    # Clean list by checking if solution converged
    cleanOffsetWSs = [WS+(offset*row) for WS in dropOnOtherList(WSs, Cs)]
    cleanWes = dropOnOtherList(Wes, Cs)
    plot(cleanOffsetWSs, cleanWes, "k")
    
###### INTERSECTION CURVES
# Takeoff Field Length
cleanOffsetWSs = [WS for WS in dropOnOtherList(WSs, Cs)]
params, pconv = curve_fit(fit_func, cleanOffsetWSs, W0fromdT0Intersection, p0=(1, 0))
plot(fWS, [exponentialForm(WS, params[0], params[1]) for WS in fWS], label="Takeoff Field Length")

# Landing Field Length
cleanOffsetWSs = [WS for WS in dropOnOtherList(WSs, Cs)]
params, pconv = curve_fit(fit_func, cleanOffsetWSs, W0fromdLIntersection, p0=(1, 0))
plot(fWS, [exponentialForm(WS, params[0], params[1]) for WS in fWS], label="Landing Field Length")

# Flight Time
cleanOffsetWSs = [WS for WS in dropOnOtherList(WSs, Cs)]
params, pconv = curve_fit(fit_func, cleanOffsetWSs, W0fromTIntersection, p0=(1, 0))
plot(fWS, [exponentialForm(WS, params[0], params[1]) for WS in fWS], label="Flight Time")

title("Carpet Plot")
xlabel("Wing Loading [lb/ft^2]")
ylabel("Empty Weight [lb]")
legend()

################################################################################

show()
