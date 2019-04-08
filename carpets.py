from utilities import *

################################################################################
# CARPET PLOTS
################################################################################

###### Create sizing matrix
# Obtain center cell W/S and T/W from guess or previous best carpet plot result
WS = convert(50, "lb/ft^2", "N/m^2")
TW = 1 # convert(0.072, "hp/lb", "W/N") # TODO: validate this number, it's power to weight though. but T/W should not be 1!

# Driving parameters
WS_matrix = [WS * 0.8, WS, WS * 1.2]
TW_matrix = [TW * 0.8, TW, TW * 1.2]

# FOR loop that iterates through 3x3 permutations of W/S and T/W and create matrix
p = [[performanceParameters([WS, TW], testcraft) for WS in WS_matrix] for TW in TW_matrix]

###### W0 TRENDS
# Create WS vs. W0 vector
W0_WS = [i[0] for i in p]

# Plot W0 as function of W/S for each T/W
figure()
plot(WS_matrix, W0_WS)
title("W0 Trends")
xlabel("W_0 / S")
ylabel("W_0")

###### CROSS PLOTS
# Plot dTO as function of W/S for each T/W
figure()
plot(WS_matrix, [i[1] for i in p])
title("Takeoff Distance")
xlabel("W_0 / S")
ylabel("d_{TO}")
# Find intersection of curve with dT0 limit

# Plot range as function of W/S for each T/W
figure()
plot(WS_matrix, [i[2] for i in p])
title("Range")
xlabel("W_0 / S")
ylabel("Range")
# Find intersection of curve with axis

# Plot flight time as function of W/S for each T/W
figure()
plot(WS_matrix, [i[4] for i in p])
title("Flight Time")
xlabel("W_0 / S")
ylabel("Flight Time")
# Find intersection of curve with axis

###### SIZING PLOT
# Plot fit curve of dTO on sizing plot
# Plot fit curve of Ps on sizing plot
