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

# Driving parameters
# WSs = [WS * 0.8, WS, WS * 1.2]
# PWs = [PW * 0.8, PW, PW * 1.2]
WSs = [WS * 0.8]
PWs = [PW * 0.8]

# FOR loop that iterates through 3x3 permutations of W/S and T/W and create matrix

ids = [[airplaneDefinitionID("testcraft", {
    "wing loading": WS,
    "power to weight ratio": PW
    }) for WS in WSs] for PW in PWs]

initialAirplanes = [[loadInitialAirplane(id) for id in row] for row in ids]
simulations = [[loadSimulation(id) for id in row] for row in ids]
finalAirplanes = [[loadFinalAirplane(id) for id in row] for row in ids]

sim = simulations[0][0]

ps = sim["position"]
hs = sim["altitude"]

figure()
plot([convert(p, "m", "nmi") for p in ps], [convert(h, "m", "ft") for h in hs])

show()