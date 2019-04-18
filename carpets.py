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

WSs = [WS*0.8, WS*0.9, WS, WS*1.1, WS*1.2]
PWs = [PW*0.8, PW*0.9, PW, PW*1.1, PW*1.2]

# Driving Parameters (used for fit curves)
fit_WS = linspace(WS*0.7, WS*1.3, 1000)
fit_PW = linspace(PW*0.7, PW*1.3, 1000)

# AIRPLANE

airplaneName = "tecnam"

# GET DRIVING PARAMETERS

p = [[getPerformanceParameters(airplaneName, {
    "wing loading": WS,
    "power to weight ratio": PW
    }, designMission) for WS in WSs] for PW in PWs]

# make matrix for each driving parameter independently

pWS = [[convert(WS, "N/m^2", "lb/ft^2") for WS in copy(WSs)] for PW in PWs]
pPW = transpose([[convert(PW, "W/N", "hp/lb") for PW in copy(PWs)] for WS in WSs])
fWS = [convert(WS, "N/m^2", "lb/ft^2") for WS in fit_WS]
fPW = [convert(PW, "W/N", "hp/lb") for PW in fit_PW]

# make matrix for each performance parameter independently

pC = [[PP["converged"] for PP in row] for row in p] # Verification that simulation converged at this value
pWe = [[convert(PP["empty weight"], "N", "lb") for PP in row] for row in p]
pdT0 = [[convert(PP["takeoff field length"], "m", "ft") for PP in row] for row in p]
pR = [[convert(PP["range"], "m", "nmi") for PP in row] for row in p]
pV = [[convert(PP["average ground speed"], "m/s", "kts") for PP in row] for row in p]
pT = [[convert(PP["flight time"], "s", "hr") for PP in row] for row in p]
pF = [[convert(PP["fuel used"], "N", "lb") for PP in row] for row in p]

################################################################################
# GROSS WEIGHT TRENDS
################################################################################

# FOR loop that iterates through 3x3 permutations of W/S and T/W and create matrix

###### W0 TRENDS
W0FitParameters = []
# Plot W0 as function of W/S for each T/W
figure()

for (Cs, Wes, WSs) in zip(pC, pWe, pWS): # for each row
    # Clean list by checking if solution converged
    cleanWes = dropOnOtherList(Wes, Cs)
    cleanWSs = dropOnOtherList(WSs, Cs)
    W0params, pconv = curve_fit(fit_func, cleanWSs, cleanWes, p0=(1, 0))
    a, b = (W0params[0], W0params[1])
    
    plot(cleanWes, cleanWSs, "k.")
    plot([exponentialForm(WS, a, b) for WS in fWS], fWS, "k-")
    W0FitParameters.append(W0params)

title("Empty Weight Trends")
ylabel("Wing Loading [lb/ft^2]")
xlabel("Gross Weight [lb]")
# 
# ################################################################################
# # LANDING DISTANCE CROSS PLOT
# ################################################################################
# 
# ###### CROSS PLOTS
# W0fromdT0Intersection = []
# W0fromRangeIntersection = []
# W0fromFlightTimeIntersection = []
# 
# # Plot dTO as function of W/S for each P/W
# figure()
# for row, PWlist in enumerate(p):
#     # Clean list by checking if solution converged
#     dirtydT0 = [convert(i["takeoff field length"], "m", "ft") for i in PWlist]
#     cleandT0 = dropOnOtherList(dirtydT0, converged[row])
#     dirtyWSs = [convert(WS, "N/m^2", "lb/ft^2") for WS in WSs]
#     cleanWSs = dropOnOtherList(dirtyWSs, converged[row])
# 
#     # Plot points and curve fit
#     plot(cleanWSs, cleandT0, ".")
#     params, pconv = curve_fit(fit_func, cleanWSs, cleandT0, p0=(1, 0))
#     # plot(fit_WS, [exponentialForm(WS, params[0], params[1]) for WS in fit_WS])
# 
#     # Find intersection of curve with dT0 limit
#     WS_dT0Intersection = invExponentialForm(minimumTakeoffFieldLength, params[0], params[1])
#     W0_WS_dT0Intersection = invExponentialForm(WS_dT0Intersection, W0FitParameters[row][0], W0FitParameters[row][1])
#     W0fromdT0Intersection.append(W0_WS_dT0Intersection)
# 
# # hlines(minimumTakeoffFieldLength, fit_WS[0], fit_WS[-1])
# 
# title("Takeoff Distance")
# xlabel("Wing Loading [N/m^2]")
# ylabel("Takeoff Field Length [ft]")
# # Find intersection of curve with dT0 limit
# 
# ################################################################################
# # RANGE CROSS PLOT
# ################################################################################
# 
# # Plot range as function of W/S for each P/W
# inc = 0
# figure()
# for PWlist in p:
#     plot(WSs, [i["range"] for i in PWlist], "k.")
#     params, pconv = curve_fit(fit_func, WSs, [i["range"] for i in PWlist], p0=(1, 0))
#     plot(fit_WS, [exponentialForm(WS, params[0], params[1]) for WS in fit_WS])
# 
#     # Find intersection of curve with range limit
#     W0_rangeIntersection = invExponentialForm(minimumRange, params[0], params[1])
#     W0_WS_rangeIntersection = invExponentialForm(W0_rangeIntersection, W0FitParameters[inc][0], W0FitParameters[inc][1])
#     W0fromRangeIntersection.append(W0_WS_rangeIntersection)
# 
#     inc = inc+1
# 
# hlines(minimumRange, fit_WS[0], fit_WS[-1])
# 
# title("Range")
# xlabel("Wing Loading [N/m^2]")
# ylabel("Range [m]")
# # Find intersection of curve with axis
# 
# ################################################################################
# # FLIGHT TIME CROSS PLOT
# ################################################################################
# 
# # Plot flight time as function of W/S for each P/W
# inc = 0
# figure()
# for PWlist in p:
#     plot(WSs, [i["flight time"] for i in PWlist], "k.")
#     params, pconv = curve_fit(fit_func, WSs, [i["flight time"] for i in PWlist], p0=(1, 0))
#     plot(fit_WS, [exponentialForm(WS, params[0], params[1]) for WS in fit_WS])
# 
#     # Find intersection of curve with flight time limit
#     W0_flightTimeIntersection = invExponentialForm(maximumFlightTime, params[0], params[1])
#     W0_WS_flightTimeIntersection = invExponentialForm(W0_flightTimeIntersection, W0FitParameters[inc][0], W0FitParameters[inc][1])
#     W0fromFlightTimeIntersection.append(W0_WS_flightTimeIntersection)
# 
#     inc=inc+1
# 
# hlines(maximumFlightTime, fit_WS[0], fit_WS[-1])
# 
# title("Flight Time")
# xlabel("Wing Loading [N/m^2]")
# ylabel("Flight Time [s]")
# # Find intersection of curve with axis
# 
# ################################################################################
# # SIZING PLOT
# ################################################################################
# 
# ###### SIZING PLOT
# # Plot fit curve intersections on sizing plot
# 
# emptyWeights = [[a["empty weight"] for a in row] for row in p]
# wingLoadings = [copy(WSs) for row in p]
# 
# figure()
# for (ews, wss) in zip(emptyWeights, wingLoadings):
#     plot(ews, wss, "k")
# 
# for (ews, wss) in zip(transpose(emptyWeights), transpose(wingLoadings)):
#     plot(ews, wss, "k")
# 
# 
# 
# title("Carpet Plot")
# xlabel("Wing Loading")
# ylabel("Empty Weight")

################################################################################

show()
