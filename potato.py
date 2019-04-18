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
# CG PLACEMENT GRAPH
################################################################################

def drawCGPotato(airplaneName, drivingParameters):
    initialAirplane = defineAirplane(airplaneName, drivingParameters)
    finalAirplane = simulateAirplane(initialAirplane, designMission)
    id = airplaneDefinitionID(airplaneName, drivingParameters)
    simulation = loadSimulation(id)
    
    figure()
    plot([convert(CG, "m", "ft") for CG in CGs], [convert(W, "N", "lb") for W in Ws])
    # TODO: draw stability bounds
    xlabel("C.G. [ft]")
    ylabel("Weight [lb]")
    
    show()