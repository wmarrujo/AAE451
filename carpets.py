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

# FOR loop that iterates through 3x3 permutations of W/S and T/W and create matrix

p = [[getPerformanceParameters("testcraft", {
    "wing loading": WS,
    "power to weight ratio": PW
    }, designMission) for WS in WSs] for PW in PWs]

###### W0 TRENDS

# Plot W0 as function of W/S for each T/W
figure()
plot(WSs, [i["empty weight"] for i in p[0]], ".")
plot(WSs, [i["empty weight"] for i in p[1]], ".")
plot(WSs, [i["empty weight"] for i in p[2]], ".")
title("W0 Trends")
ylabel("Wing Loading [N/m^2]")
xlabel("Gross Weight [N]")

###### CROSS PLOTS

fit_WS = linspace(WS*0.5, WS*1.5, 1000)
fit_PW = linspace(PW*0.5, PW*1.5, 1000)
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
offset = convert(4, "lb/ft^2", "N/m^2")
inc = 0;
temp_emptyWeight = []
temp_offset_WS = []

figure()
for PWlist in p:
    emptyWeightList = [i["empty weight"] for i in PWlist]
    plot(WSs, emptyWeightList, "k.")
    offset_WS = linspace((WS*0.5)+offset*inc, (WS*1.5)+offset*inc, 1000)
    params, pconv = optimize.curve_fit(fit_func, WSs, [i["empty weight"] for i in PWlist], p0=(1, 0))
    fit_emptyWeight = [exponentialForm(WS, params[0], params[1]) for WS in fit_WS]
    plot(offset_WS, fit_emptyWeight, "k")
    
    temp_emptyWeight.append(offset_WS[0])
    temp_offset_WS.append(emptyWeightList)
    
    inc = inc+1

print(temp_emptyWeight)
print(temp_offset_WS)

title("Carpet Plot")
ylabel("Empty Weight")

show()
