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
# CARPET PLOTS
################################################################################

def fit_func(xs, a, b):
    return [exponentialForm(x, a, b) for x in xs]

def exponentialForm(x, a, b):
    return a * exp(b * x)
    
def invExponentialForm(y, a, b):
    return log(y / a) / b

###### Create sizing matrix
# Obtain center cell W/S and T/W from guess or previous best carpet plot result
WS = convert(50, "lb/ft^2", "N/m^2")
PW = convert(0.072, "hp/lb", "W/N")

# Driving parameters
WSs = [WS * 0.8, WS, WS * 1.2]
PWs = [PW * 0.8, PW, PW * 1.2]

fit_WS = linspace(WS*0.5, WS*1.5, 1000)
fit_PW = linspace(PW*0.5, PW*1.5, 1000)

# FOR loop that iterates through 3x3 permutations of W/S and T/W and create matrix

p = [[getPerformanceParameters("testcraft", {
    "wing loading": WS,
    "power to weight ratio": PW
    }, designMission) for WS in WSs] for PW in PWs]

###### W0 TRENDS
W0FitParameters = []
# Plot W0 as function of W/S for each T/W
figure()

for PWlist in p:
    plot(WSs, [i["empty weight"] for i in PWlist], "k.")
    W0params, pconv = curve_fit(fit_func, WSs, [i["empty weight"] for i in PWlist], p0=(1, 0))
    plot(fit_WS, [exponentialForm(WS, W0params[0], W0params[1]) for WS in fit_WS])
    
    W0FitParameters.append(W0params)
print(W0FitParameters)
title("W0 Trends")
ylabel("Wing Loading [N/m^2]")
xlabel("Gross Weight [N]")

###### CROSS PLOTS
dT0s = []
ranges = []
flightTimes = []

# Plot dTO as function of W/S for each P/W
figure()
for PWlist in p:
    plot(WSs, [i["takeoff distance"] for i in PWlist], "k.")
    params, pconv = curve_fit(fit_func, WSs, [i["takeoff distance"] for i in PWlist], p0=(1, 0))
    plot(fit_WS, [exponentialForm(WS, params[0], params[1]) for WS in fit_WS])
    
    # Find intersection of curve with dT0 limit
    dT0Intersection = invExponentialForm(minimumTakeoffFieldLength, params[0], params[1])
    dT0s.append(dT0Intersection)
hlines(minimumTakeoffFieldLength, fit_WS[0], fit_WS[-1])

title("Takeoff Distance")
xlabel("Wing Loading [N/m^2]")
ylabel("Takeoff Distance [m]")

# Plot range as function of W/S for each P/W
figure()
for PWlist in p:
    plot(WSs, [i["range"] for i in PWlist], "k.")
    params, pconv = curve_fit(fit_func, WSs, [i["range"] for i in PWlist], p0=(1, 0))
    plot(fit_WS, [exponentialForm(WS, params[0], params[1]) for WS in fit_WS])
    
    # Find intersection of curve with range limit
    rangeIntersection = invExponentialForm(minimumRange, params[0], params[1])
    ranges.append(rangeIntersection)
hlines(minimumRange, fit_WS[0], fit_WS[-1])

title("Range")
xlabel("Wing Loading [N/m^2]")
ylabel("Range [m]")

# Plot flight time as function of W/S for each P/W
figure()
for PWlist in p:
    plot(WSs, [i["flight time"] for i in PWlist], "k.")
    params, pconv = curve_fit(fit_func, WSs, [i["flight time"] for i in PWlist], p0=(1, 0))
    plot(fit_WS, [exponentialForm(WS, params[0], params[1]) for WS in fit_WS])
    
    # Find intersection of curve with flight time limit
    flightTimeIntersection = invExponentialForm(maximumFlightTime, params[0], params[1])
    flightTimes.append(flightTimeIntersection)
hlines(maximumFlightTime, fit_WS[0], fit_WS[-1])

title("Flight Time")
xlabel("Wing Loading [N/m^2]")
ylabel("Flight Time [s]")

###### SIZING PLOT
# Plot fit curve intersections on sizing plot

emptyWeights = [[a["empty weight"] for a in row] for row in p]
wingLoadings = [copy(WSs) for row in p]

figure()
for (ews, wss) in zip(emptyWeights, wingLoadings):
    plot(ews, wss, "k")

for (ews, wss) in zip(transpose(emptyWeights), transpose(wingLoadings)):
    plot(ews, dT0s)
    plot(ews, wss, "k")

title("Carpet Plot")
xlabel("Wing Loading")
ylabel("Empty Weight")

show()
