from convert import convert
from matplotlib.pyplot import *
from scipy import *
from stdatmo import *
from csvTools import *

import sys
sys.path.insert(0, sys.path[0] + "./sizing")
from testConfig import *

################################################################################
# CARPET PLOTS
################################################################################

###### Create carpet plot matrix
# Obtain center cell W/S and T/W from guess or previous best carpet plot result
WS = convert(50, "lb/ft^2", "N/m^2")
TW = 1
# Create vector of W/S with elements [W/S * 0.9, W/S, W/S * 1.1]
WS_matrix = np.array([WS * 0.9, WS, WS * 1.1])
print(WS_matrix)
# Create vector of TW with elements [T/W * 0.1, T/W, T/W * 1.1]
TW_matrix = [TW * 0.9, TW, TW * 1.1]
print(TW_matrix)
# FOR loop that iterates through 3x3 permutations of W/S and T/W
for i, wingLoading in enumerate(WS_matrix):
    for j, thrustToWeight in enumerate(TW_matrix):
    # run simulation at single W/S and T/W combination
        print("WS:{}, TW:{}".format(wingLoading, thrustToWeight))
        defineAirplane([wingLoading, thrustToWeight])
    # store simulation W0, dTO, and Ps in (i,j) cell of block matrix

###### W0 TRENDS
# Plot W0 as function of W/S for each T/W

###### CROSS PLOTS
# Plot dTO as function of W/S for each T/W
# Find intersection of curve with dT0 limit

# Plot Ps as function of W/S for each T/W
# Find intersection of curve with axis

###### SIZING PLOT
# Plot fit curve of dTO on sizing plot
# Plot fit curve of Ps on sizing plot
