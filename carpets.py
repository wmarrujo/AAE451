from utilities import *

################################################################################
# FUNCTIONS
################################################################################

def performanceParameters(drivingParameters, defaultAirplane):
    """Calculate the aircraft performance for each driving parameter combination"""
    
    # DEFINE AIRPLANE
    
    airplane = defineAirplane(drivingParameters, defaultAirplane) # Here's the airplane we're going to simulate
    
    # GET INITIAL AIRPLANE PERFORMANCE PARAMETERS
    
    emptyWeight = airplane.emptyWeight #Grab the airplane configuration before it starts simulating stuff
    
    # SIMULATE MISSION
    
    filename = "./data/simulations/" + airplane.name + str(compareValue(drivingParameters)) + ".csv" # make unique filename based on driving parameters
    #TODO verify if function exists for same inputs (then just use that file, otherwise continue to simulate)
    writeCSVLine(filename, ["time", "segment", "weight", "fuelWeight"]) # write header line to CSV files
    designMission.simulate(1, airplane, lambda t, s, a: recordingFunction(t, s, a, filename)) # simulate the airplane
    simulation = CSVToDict(filename) # store this run of the simulation to a dictionary
    
    # GET PERFORMANCE PARAMETERS FROM SIMULATION
    
    dTO  = simulation["position"][simulation.index(first(simulation["altitude"], condition = lambda altitude: altitude >= 50))]
    range = simulation["position"][-1]
    
    cruiseStartPosition  = simulation["position"][simulation.index(first(simulation["segment"], condition = lambda segment: segment == "cruise"))]
    cruiseStartTime  = simulation["time"][simulation.index(first(simulation["segment"], condition = lambda segment: segment == "cruise"))]
    cruiseEndPosition  = simulation["position"][simulation.index(first(reversed(simulation["segment"]), condition = lambda segment: segment == "cruise"))]
    cruiseEndTime  = simulation["time"][simulation.index(first(reversed(simulation["segment"]), condition = lambda segment: segment == "cruise"))]
    groundSpeed = (cruiseEndPosition - cruiseStartPosition) / (cruiseEndTime - cruiseStartTime)
    flightTime = cruiseEndTime - cruiseStartTime
    
    fuelUsed  = simulation["fuelWeight"][0] - simulation["fuelWeight"][-1]
    
    # RETURN PERFORMANCE PARAMETERS
    
    return [emptyWeight, dTO, range, groundSpeed, flightTime, fuelUsed]

def defineAirplane(drivingParameters, defaultAirplane):
    """Apply the driving parameters to the relevant airplane parameters"""
    airplane = copy.deepcopy(defaultAirplane)
    
    # Empty Weight
    airplane.emptyWeight = WS * airplane.wing.span # Keep span constant
    
    return airplane

def recordingFunction(t, segmentTitle, airplane, filename):
    """Records a single line (time step) in the CSV file during simulation"""
    # Stuff you need to calculate performance parameters
    W = AirplaneWeight(airplane)
    d = airplane.position
    h = airplane.altitude
    thrust = AirplaneThrust(airplane)
    
    writeLineToFile(filename, [t, segmentTitle, W]) # write line to CSV file (don't forget to add each element)

################################################################################
# CARPET PLOTS
################################################################################

###### Create sizing matrix
# Obtain center cell W/S and T/W from guess or previous best carpet plot result
WS = convert(50, "lb/ft^2", "N/m^2")
TW = 1

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
