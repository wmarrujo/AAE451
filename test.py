import sys
import os
sys.path.append(os.path.join(sys.path[0], "configurations"))
from testcraft import airplane as testcraft
from utilities import *
from constants import *
from parameters import *
from missions import *
from equations import *
from sizing import *
from matplotlib.pyplot import *



DPS = [convert(50, "lb/ft^2", "N/m^2"), 1]

testcraft.InitialGrossWeight = convert(3000, "lb", "N")
initialWeight = AirplaneWeight(testcraft)
initialFuelWeight = FuelWeight(testcraft)

simulation = {"time":[], "segment":[], "x":[], "h":[], "g":[], "p":[], "v":[]}
def recordSimulation(t, s, a):
    simulation["time"].append(t)
    simulation["segment"].append(s)
    simulation["x"].append(a.position)
    simulation["h"].append(a.altitude)
    simulation["g"].append(a.flightPathAngle)
    simulation["p"].append(a.pitch)
    simulation["v"].append(a.speed)

success = designMission.simulate(1, testcraft, recordSimulation)




print("Mission Finished" if success else "Mission Failed")
print("W0i: {} lb - W0: {} lb - Wf: {} lb - WFi: {} lb - WFf: {} lb - We: {} lb - Wpay: {} lb".format(
    convert(testcraft.initialGrossWeight, "N", "lb"),
    convert(initialWeight, "N", "lb"),
    convert(AirplaneWeight(testcraft), "N", "lb"),
    convert(initialFuelWeight, "N", "lb"),
    convert(FuelWeight(testcraft), "N", "lb"),
    convert(EmptyWeight(testcraft), "N", "lb"),
    convert(PayloadWeight(testcraft), "N", "lb")))

ts_hr = [convert(t, "s", "hr") for t in simulation["time"]]
xs_nmi = [convert(x, "m", "nmi") for x in simulation["x"]]
hs_ft = [convert(h, "m", "ft") for h in simulation["h"]]

figure()
plot(xs_nmi, hs_ft, "k-")
title("Track")

figure()
plot(ts_hr, hs_ft, "k-")
title("Altitude History")

show()