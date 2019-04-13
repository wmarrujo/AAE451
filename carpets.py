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
# Plot dTO as function of W/S for each P/W
figure()
plot(WSs, [i["takeoff distance"] for i in p[0]], ".")
plot(WSs, [i["takeoff distance"] for i in p[1]], ".")
plot(WSs, [i["takeoff distance"] for i in p[2]], ".")

params, pconv = curve_fit(fit_func, WSs, [i["takeoff distance"] for i in p[0]], p0=(1, 0))
print("params", params)
plot(WSs, [exponentialForm(WS, params[0], params[1]) for WS in WSs], "C0")

title("Takeoff Distance")
xlabel("Wing Loading [N/m^2]")
ylabel("Takeoff Distance [m]")
# Find intersection of curve with dT0 limit

# Plot range as function of W/S for each P/W
figure()
plot(WSs, [i["range"] for i in p[0]], ".")
plot(WSs, [i["range"] for i in p[1]], ".")
plot(WSs, [i["range"] for i in p[2]], ".")

f = poly1d(polyfit(WSs, [i["range"] for i in p[0]], 3))
x_new = linspace(WSs[0], WSs[-1], 50)
y_new = f(x_new)
plot(x_new, y_new, "C0")
f = poly1d(polyfit(WSs, [i["range"] for i in p[1]], 3))
x_new = linspace(WSs[0], WSs[-1], 50)
y_new = f(x_new)
plot(x_new, y_new, "C1")
f = poly1d(polyfit(WSs, [i["range"] for i in p[2]], 3))
x_new = linspace(WSs[0], WSs[-1], 50)
y_new = f(x_new)
plot(x_new, y_new, "C2")

title("Range")
xlabel("Wing Loading [N/m^2]")
ylabel("Range [m]")
# Find intersection of curve with axis

# Plot flight time as function of W/S for each P/W
figure()
plot(WSs, [i["flight time"] for i in p[0]], ".")
plot(WSs, [i["flight time"] for i in p[1]], ".")
plot(WSs, [i["flight time"] for i in p[2]], ".")

f = poly1d(polyfit(WSs, [i["flight time"] for i in p[0]], 3))
x_new = linspace(WSs[0], WSs[-1], 50)
y_new = f(x_new)
plot(x_new, y_new, "C0")
f = poly1d(polyfit(WSs, [i["flight time"] for i in p[1]], 3))
x_new = linspace(WSs[0], WSs[-1], 50)
y_new = f(x_new)
plot(x_new, y_new, "C1")
f = poly1d(polyfit(WSs, [i["flight time"] for i in p[2]], 3))
x_new = linspace(WSs[0], WSs[-1], 50)
y_new = f(x_new)
plot(x_new, y_new, "C2")

title("Flight Time")
xlabel("Wing Loading [N/m^2]")
ylabel("Flight Time [s]")
# Find intersection of curve with axis

###### SIZING PLOT
# Plot fit curve of dTO on sizing plot

# Plot fit curve of Ps on sizing plot

show()
