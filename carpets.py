from utilities import *

from sizing import *

from matplotlib.pyplot import *
import sys
import os
root = os.path.join(sys.path[0], "..")
sys.path.append(root)
from testcraft import airplane as testcraft

################################################################################
# CARPET PLOTS
################################################################################

###### Create sizing matrix
# Obtain center cell W/S and T/W from guess or previous best carpet plot result
WS = convert(50, "lb/ft^2", "N/m^2")
PW = convert(0.072, "hp/lb", "W/N")

# Driving parameters
WSs = [WS * 0.8, WS, WS * 1.2]
PWs = [PW * 0.8, PW, PW * 1.2]

# FOR loop that iterates through 3x3 permutations of W/S and T/W and create matrix
p = [[getPerformanceParameters([WS, PW], testcraft) for WS in WSs] for PW in PWs]

###### W0 TRENDS

# Plot W0 as function of W/S for each T/W
figure()
plot([i["empty weight"] for i in p[0]], WSs)
plot([i["empty weight"] for i in p[1]], WSs)
plot([i["empty weight"] for i in p[2]], WSs)
title("W0 Trends")
ylabel("Wing Loading [N/m^2]")
xlabel("Gross Weight [N]")

###### CROSS PLOTS
# Plot dTO as function of W/S for each T/W
figure()
plot([i["takeoff distance"] for i in p[0]], WSs)
plot([i["takeoff distance"] for i in p[1]], WSs)
plot([i["takeoff distance"] for i in p[2]], WSs)
title("Takeoff Distance")
ylabel("Wing Loading [N/m^2]")
xlabel("Takeoff Distance [m]")
# Find intersection of curve with dT0 limit

# Plot range as function of W/S for each T/W
figure()
plot([i["range"] for i in p[0]], WSs)
plot([i["range"] for i in p[1]], WSs)
plot([i["range"] for i in p[2]], WSs)
title("Range")
ylabel("Wing Loading [N/m^2]")
xlabel("Range [m]")
# Find intersection of curve with axis

# Plot flight time as function of W/S for each T/W
figure()
plot([i["flight time"] for i in p[0]], WSs)
plot([i["flight time"] for i in p[1]], WSs)
plot([i["flight time"] for i in p[2]], WSs)
title("Flight Time")
ylabel("Wing Loading [N/m^2]")
xlabel("Flight Time [s]")
# Find intersection of curve with axis

###### SIZING PLOT
# Plot fit curve of dTO on sizing plot
# Plot fit curve of Ps on sizing plot

show()
