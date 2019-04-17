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

id = airplaneDefinitionID("tecnamHYBRID", DPS)
airplane = loadFinalAirplane(id)
simulation = loadSimulation(id)

print("empty weight:            {:.0f} lb".format(convert(PPs["empty weight"], "N", "lb")))
print("takeoff field length:    {:.0f} ft".format(convert(PPs["takeoff field length"], "m", "ft")))
print("range:                   {:.2f} nmi".format(convert(PPs["range"], "m", "nmi")))
print("average ground speed:    {:.0f} kts".format(convert(PPs["average ground speed"], "m/s", "kts")))
print("flight time:             {:.1f} hr".format(convert(PPs["flight time"], "s", "hr")))
print("fuel used:               {:.0f} lb".format(convert(PPs["fuel used"]*g, "N", "lb")))

ts = simulation["time"]
ps = simulation["position"]
hs = simulation["altitude"]
Vs = simulation["speed"]

figure()
plot([convert(p, "m", "nmi") for p in ps], [convert(h, "m", "ft") for h in hs])
ylabel("Range [nmi]")
xlabel("Altitude [ft]")

figure()
plot([convert(t, "s", "hr") for t in ts], [convert(V, "m/s", "kts") for V in Vs])
ylabel("Aircraft Speed [kts]")
xlabel("Time [s]")
show()
