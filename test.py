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
import cProfile

################################################################################
# TESTS
################################################################################

airplaneName = "tecnam"
WS = convert(20, "lb/ft^2", "N/m^2")
PW = convert(0.072, "hp/lb", "W/N")
DPS = {"wing loading": WS, "power to weight ratio": PW}
# cProfile.run("PPs = getPerformanceParameters(airplaneName, DPS, designMission)")
PPs = getPerformanceParameters(airplaneName, DPS, designMission)

id = airplaneDefinitionID(airplaneName, DPS)
airplane = loadFinalAirplane(id)
simulation = loadSimulation(id)

print("empty weight:            {:.0f} lb".format(convert(PPs["empty weight"], "N", "lb")))
print("takeoff field length:    {:.0f} ft".format(convert(PPs["takeoff field length"], "m", "ft")))
print("range:                   {:.2f} nmi".format(convert(PPs["range"], "m", "nmi")))
print("average ground speed:    {:.0f} kts".format(convert(PPs["average ground speed"], "m/s", "kts")))
print("flight time:             {:.1f} hr".format(convert(PPs["flight time"], "s", "hr")))
print("fuel used:               {:.0f} lb".format(convert(PPs["fuel used"]*g, "N", "lb")))

# for c in airplane.components:
#     print(type(c))
#     print("weight: ", convert(c.mass*g, "N", "lb"))

ts = simulation["time"]
ps = simulation["position"]
hs = simulation["altitude"]
Vs = simulation["speed"]
Ws = simulation["weight"]
CGs = simulation["cg"]

figure()
plot([convert(p, "m", "nmi") for p in ps], [convert(h, "m", "ft") for h in hs])
xlabel("Range [nmi]")
ylabel("Altitude [ft]")

figure()
plot([convert(t, "s", "hr") for t in ts], [convert(V, "m/s", "kts") for V in Vs])
xlabel("Time [hr]")
ylabel("Speed [kts]")

figure()
plot([convert(CG, "m", "ft") for CG in CGs], [convert(W, "N", "lb") for W in Ws])
xlabel("C.G. [ft]")
ylabel("Weight [lb]")

show()
