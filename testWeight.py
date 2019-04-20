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
from Cessna172 import defineAirplane as defineAirplaneObj

# EXTERNAL DEPENDENCIES

from matplotlib.pyplot import *
import cProfile

################################################################################
# TESTS
################################################################################
WS = convert(20, "lb/ft^2", "N/m^2")
PW = convert(0.072, "hp/lb", "W/N")
W0 = convert(2770 , "lb", "N")
Wf = convert(318 , "lb", "N")
DPS = {"wing loading": WS, "power to weight ratio": PW, "initial gross weight": W0, "initial fuel weight": Wf}
# cProfile.run("PPs = getPerformanceParameters(airplaneName, DPS, designMission)")
airplane = defineAirplaneObj(DPS)
