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

WS = convert(17.5, "lb/ft^2", "N/m^2")
PW = convert(0.072, "hp/lb", "W/N")
DPS = {"wing loading": WS, "power to weight ratio": PW}
PPs = getPerformanceParameters("tecnamHYBRID", DPS, designMission)

print("empty weight {} lb".format(convert(PPs["empty weight"], "N", "lb")))
print("takeoff feild length {} ft".format(convert(PPs["takeoff feild length"], "m", "ft")))
print("range {} nmi".format(convert(PPs["range"], "m", "nmi")))
print("average ground speed {} kts".format(convert(PPs["average ground speed"], "m/s", "kts")))
print("flight time {} hr".format(convert(PPs["flight time"], "s", "hr")))
print("fuel used {} lb".format(convert(PPs["fuel used"]*g, "N", "lb")))

ID = airplaneDefinitionID("tecnamHYBRID", DPS)
plane = loadFinalAirplane(ID)
sim = loadSimulation(ID)
xloc = sim["position"]
yloc = sim["altitude"]
time = sim["time"]
speed = sim["speed"]


figure()
plot(xloc, yloc)
ylabel("Range (m)")
xlabel("Altitude (m)")

figure()
plot(time, [convert(s, "m/s", "kts") for s in speed])
ylabel("Aircraft Speed (kts)")
xlabel("Time (s)")
show()
