from utilities import *

from sizing import *

from matplotlib.pyplot import *
import sys
import os
sys.path.append(os.path.join(sys.path[0], "configurations"))
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
plot(WSs, [i["empty weight"] for i in p[0]])
plot(WSs, [i["empty weight"] for i in p[1]])
plot(WSs, [i["empty weight"] for i in p[2]])
title("W0 Trends")
xlabel("Wing Loading [N/m^2]")
ylabel("Gross Weight [N]")

###### CROSS PLOTS
# Plot dTO as function of W/S for each T/W
figure()
plot(WSs, [i["takeoff distance"] for i in p[0]])
plot(WSs, [i["takeoff distance"] for i in p[1]])
plot(WSs, [i["takeoff distance"] for i in p[2]])
title("Takeoff Distance")
xlabel("Wing Loading [N/m^2]")
ylabel("Takeoff Distance [m]")
# Find intersection of curve with dT0 limit

# Plot range as function of W/S for each T/W
figure()
plot(WSs, [i["range"] for i in p[0]])
plot(WSs, [i["range"] for i in p[1]])
plot(WSs, [i["range"] for i in p[2]])
title("Range")
xlabel("Wing Loading [N/m^2]")
ylabel("Range [m]")
# Find intersection of curve with axis

# Plot flight time as function of W/S for each T/W
figure()
plot(WSs, [i["flight time"] for i in p[0]])
plot(WSs, [i["flight time"] for i in p[1]])
plot(WSs, [i["flight time"] for i in p[2]])
title("Flight Time")
xlabel("Wing Loading [N/m^2]")
ylabel("Flight Time [s]")
# Find intersection of curve with axis

###### SIZING PLOT
# Plot fit curve of dTO on sizing plot
# Plot fit curve of Ps on sizing plot

show()