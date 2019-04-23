# PATHS

import sys
import os
hereDirectory = os.path.dirname(os.path.abspath(__file__))
rootDirectory = os.path.join(hereDirectory, "..")
sys.path.append(rootDirectory)

# LOCAL DEPENDENCIES

from utilities import *

from constants import *
from parameters import *
from missions import *
from equations import *
from sizing import *

# EXTERNAL DEPENDENCIES

from matplotlib.pyplot import *

################################################################################
# TESTS
################################################################################

airplaneName = "Gopher"
drivingParameters = {
    "wing loading": convert(20, "lb/ft^2", "N/m^2"),
    "power to weight ratio": convert(0.072, "hp/lb", "W/N")}
definingParameters = dict(drivingParameters, **{
    "initial gross weight": convert(2711, "lb", "N"),
    "initial fuel weight": convert(300, "lb", "N")})

id = airplaneDefinitionID(airplaneName, drivingParameters)
defineSpecificAirplane = airplaneDefinitionFunction(airplaneName)
# initialAirplane = defineSpecificAirplane(definingParameters)
closureResult = closeAircraftDesign(defineSpecificAirplane, drivingParameters, designMission)
closedAirplane = closureResult["airplane"]
closed = closureResult["closed"]

simulationResults = simulateAirplane(closedAirplane, designMission)
initialAirplane = simulationResults["initial airplane"]
simulation = simulationResults["simulation"]
finalAirplane = simulationResults["final airplane"]
performanceParameters = getPerformanceParameters(initialAirplane, simulation, finalAirplane)
print(performanceParameters)