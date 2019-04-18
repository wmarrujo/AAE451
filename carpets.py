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
PW = convert(0.08, "hp/lb", "W/N")

# DRIVNG PARAMETERS MATRIX

WSs = [WS * 0.8, WS,  WS * 1.2]
PWs = [PW * 0.8, PW, PW * 1.2]

# Driving Parameters (used for fit curves)
fit_WS = linspace(WS*0.5, WS*1.5, 1000)
fit_PW = linspace(PW*0.5, PW*1.5, 1000)

# AIRPLANE

airplaneName = "tecnam"

# GET DRIVING PARAMETERS

p = [[getPerformanceParameters(airplaneName, {
    "wing loading": WS,
    "power to weight ratio": PW
    }, designMission) for WS in WSs] for PW in PWs]

# make matrix for each driving parameter independently

pWS = [copy(WSs) for PW in PWs]
pPW = transpose([copy(PWs) for WS in WSs])

# make matrix for each performance parameter independently

converged = [[PP["converged"] for PP in row] for row in p] # Verification that simulation converged at this value
pWe = [[PP["empty weight"] for PP in row] for row in p]

################################################################################
# GROSS WEIGHT TRENDS
################################################################################

# FOR loop that iterates through 3x3 permutations of W/S and T/W and create matrix

###### W0 TRENDS
W0FitParameters = []
# Plot W0 as function of W/S for each T/W
figure()

for row, PWlist in enumerate(p):
    # Clean list by checking if solution converged
    dirtyW0s = [convert(i["empty weight"], "N", "lb") for i in PWlist]
    cleanW0s = dropOnOtherList(dirtyW0s, converged[row])
    dirtyWSs = [convert(WS, "N/m^2", "lb/ft^2") for WS in WSs]
    cleanWSs = dropOnOtherList(dirtyWSs, converged[row])
    
    plot(cleanW0s, cleanWSs, ".")
    W0params, pconv = curve_fit(fit_func, WSs, [i["empty weight"] for i in PWlist], p0=(1, 0))
    #plot(fit_WS, [exponentialForm(WS, W0params[0], W0params[1]) for WS in fit_WS])
    W0FitParameters.append(W0params)

title("W0 Trends")
ylabel("Wing Loading [lb/ft^2]")
xlabel("Gross Weight [lb]")

################################################################################
# CROSS PLOTS
################################################################################

###### TAKEOFF DISTANCE CROSS PLOTS
W0fromdTOIntersection = []

# Plot dTO as function of W/S for each P/W
figure()
for row, PWlist in enumerate(p):
    # Clean list by checking if solution converged
    dirtydTO = [convert(i["takeoff field length"], "m", "ft") for i in PWlist]
    cleandTO = dropOnOtherList(dirtydTO, converged[row])
    dirtyWSs = [convert(WS, "N/m^2", "lb/ft^2") for WS in WSs]
    cleanWSs = dropOnOtherList(dirtyWSs, converged[row])
    
    # Plot points and curve fit
    plot(cleanWSs, cleandTO, ".")
    params, pconv = curve_fit(fit_func, cleanWSs, cleandTO, p0=(1, 0))
    plot(fit_WS, [exponentialForm(WS, params[0], params[1]) for WS in fit_WS])
    
    # Find intersection of curve with dTO limit
    WS_dTOIntersection = invExponentialForm(maximumFieldLength, params[0], params[1])
    W0_WS_dTOIntersection = invExponentialForm(WS_dTOIntersection, W0FitParameters[row][0], W0FitParameters[row][1])
    W0fromdTOIntersection.append(W0_WS_dTOIntersection)

hlines(maximumFieldLength, fit_WS[0], fit_WS[-1])

title("Takeoff Distance")
xlabel("Wing Loading [N/m^2]")
ylabel("Takeoff Field Length [ft]")
# Find intersection of curve with dTO limit

###### LANDING DISTANCE CROSS PLOTS
W0fromdIntersection = []

# Plot dL as function of W/S for each P/W
figure()
for row, PWlist in enumerate(p):
    # Clean list by checking if solution converged
    dirtydL = [convert(i["landing field length"], "m", "ft") for i in PWlist]
    cleandL = dropOnOtherList(dirtydL, converged[row])
    dirtyWSs = [convert(WS, "N/m^2", "lb/ft^2") for WS in WSs]
    cleanWSs = dropOnOtherList(dirtyWSs, converged[row])
    
    # Plot points and curve fit
    plot(cleanWSs, cleandL, ".")
    params, pconv = curve_fit(fit_func, cleanWSs, cleandL, p0=(1, 0))
    plot(fit_WS, [exponentialForm(WS, params[0], params[1]) for WS in fit_WS])
    
    # Find intersection of curve with dTO limit
    WS_dLIntersection = invExponentialForm(maximumFieldLength, params[0], params[1])
    W0_WS_dLIntersection = invExponentialForm(WS_dLIntersection, W0FitParameters[row][0], W0FitParameters[row][1])
    W0fromdLIntersection.append(W0_WS_dLIntersection)

hlines(maximumFieldLength, fit_WS[0], fit_WS[-1])

title("Landing Distance")
xlabel("Wing Loading [N/m^2]")
ylabel("Landing Field Length [ft]")
# Find intersection of curve with dTO limit

################################################################################
# SIZING PLOT
################################################################################

###### SIZING PLOT
# Plot fit curve intersections on sizing plot

emptyWeights = [[a["empty weight"] for a in row] for row in p]
wingLoadings = [copy(WSs) for row in p]

figure()
for (ews, wss) in zip(emptyWeights, wingLoadings):
    plot(ews, wss, "k")

for (ews, wss) in zip(transpose(emptyWeights), transpose(wingLoadings)):
    plot(ews, wss, "k")
    
title("Carpet Plot")
xlabel("Wing Loading")
ylabel("Empty Weight")

show()
