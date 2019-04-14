# PATHS

import sys
import os
hereDirectory = os.path.dirname(os.path.abspath(__file__))
rootDirectory = hereDirectory
sys.path.append(rootDirectory)

# LOCAL DEPENDENCIES

from utilities import *

from constants import *
from parameters import *
from missions import *
from equations import *
from sizing import *

sys.path.append(os.path.join(rootDirectory, "configurations"))
from testcraft import defineAirplane as defineTestcraft

# EXTERNAL DEPENDENCIES

from matplotlib.pyplot import *

################################################################################
# TESTS
################################################################################

WS = convert(50, "lb/ft^2", "N/m^2")
PW = convert(0.072, "hp/lb", "W/N")
DPS = {"wing loading": WS, "power to weight ratio": PW}
PPs = getPerformanceParameters("tecnam", DPS, designMission)
print(PPs)

ID = airplaneDefinitionID(airplaneName, drivingParameters)
plane = loadFinalAirplane(ID)
sim = loadSimulation(ID)
xloc = sim["position"]
yloc = sim["altitude"]
time = sim["time"]

figure()
plot(xloc, yloc)
ylabel("meters")
xlabel("meters")
show()
