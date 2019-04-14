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
# DEFINING AN AIRPLANE
################################################################################

DPS = {
    "wing loading": convert(50, "lb/ft^2", "N/m^2"),
    "power to weight ratio": convert(0.072, "hp/lb", "W/N")}

PPs = getPerformanceParameters("tecnam", DPS, designMission, silent=True)
print(PPs)