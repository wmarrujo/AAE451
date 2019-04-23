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
import cProfile

################################################################################
# TESTS
################################################################################

airplaneName = "Gopher"
drivingParameters = {
    "wing loading": convert(20, "lb/ft^2", "N/m^2"),
    "power to weight ratio": convert(0.072, "hp/lb", "W/N")}
# cProfile.run("PPs = getPerformanceParameters(airplaneName, DPS, designMission)")
designDict = getAirplaneDesignData(airplaneName, drivingParameters, designMission, silent=False)
referenceDict = getReferenceMissionData(airplaneName, drivingParameters, designMission, referenceMission, referenceMissionName="reference", closeReferenceMissionFunction=closeReferenceMissionByFuelWeightAndRange, silent=False)
referenceDict = getReferenceMissionData(airplaneName, drivingParameters, designMission, referenceMission, referenceMissionName="reference", silent=False)
abortedDict = getReferenceMissionData(airplaneName, drivingParameters, designMission, abortedMission, referenceMissionName="abort", silent=False)

designDict["initial airplane"].passengers = ceil(designMission.passengerFactor*designDict["initial airplane"].maxPassengers)
referenceDict["initial airplane"].passengers = ceil(referenceMission.passengerFactor*referenceDict["initial airplane"].maxPassengers)
abortedDict["initial airplane"].passengers = ceil(abortedMission.passengerFactor*abortedDict["initial airplane"].maxPassengers)

designPPs = getPerformanceParameters(designDict["initial airplane"], designDict["simulation"], designDict["final airplane"])
referencePPs = getPerformanceParameters(referenceDict["initial airplane"], referenceDict["simulation"], referenceDict["final airplane"])
abortedPPs = getPerformanceParameters(abortedDict["initial airplane"], abortedDict["simulation"], abortedDict["final airplane"])

print("---- Design Mission")
print("empty weight:            {:.0f} lb".format(convert(designPPs["empty weight"], "N", "lb")))
print("takeoff field length:    {:.0f} ft".format(convert(designPPs["takeoff field length"], "m", "ft")))
print("landing field length:    {:.0f} ft".format(convert(designPPs["landing field length"], "m", "ft")))
print("range:                   {:.2f} nmi".format(convert(designPPs["range"], "m", "nmi")))
print("average ground speed:    {:.0f} kts".format(convert(designPPs["range"]/designPPs["mission time"], "m/s", "kts")))
print("flight time:             {:.1f} hr".format(convert(designPPs["mission time"], "s", "hr")))
print("fuel used:               {:.0f} lb".format(convert(designPPs["fuel used"], "N", "lb")))
print("takeoff weight:          {:.0f} lb".format(convert(AirplaneWeight(designDict["initial airplane"]), "N", "lb")))
print("landing weight           {:.0f} lb".format(convert(AirplaneWeight(designDict["final airplane"]),"N","lb")))

print("---- Reference Mission")
print("empty weight:            {:.0f} lb".format(convert(referencePPs["empty weight"], "N", "lb")))
print("takeoff field length:    {:.0f} ft".format(convert(referencePPs["takeoff field length"], "m", "ft")))
print("landing field length:    {:.0f} ft".format(convert(referencePPs["landing field length"], "m", "ft")))
print("range:                   {:.2f} nmi".format(convert(referencePPs["range"], "m", "nmi")))
print("average ground speed:    {:.0f} kts".format(convert(referencePPs["range"]/referencePPs["mission time"], "m/s", "kts")))
print("flight time:             {:.1f} hr".format(convert(referencePPs["mission time"], "s", "hr")))
print("fuel used:               {:.0f} lb".format(convert(referencePPs["fuel used"], "N", "lb")))
print("takeoff weight:          {:.0f} lb".format(convert(AirplaneWeight(referenceDict["initial airplane"]), "N", "lb")))
print("End weight:              {:.0f} lb".format(convert(AirplaneWeight(referenceDict["final airplane"]),"N","lb")))

print("---- Aborted Mission")
print("landing field length:    {:.0f} ft".format(convert(abortedPPs["landing field length"], "m", "ft")))
print("initial gross weight:    {:.0f} lb".format(convert(AirplaneWeight(abortedDict["initial airplane"]), "N", "lb")))
print("final gross weight:      {:.0f} lb".format(convert(AirplaneWeight(abortedDict["final airplane"]), "N", "lb")))

initialDAirplane = designDict["initial airplane"]
initialRAirplane = referenceDict["initial airplane"]

print("---- Aircraft Geometry")
print("wing")
print("span:                    {:.3f} ft".format(convert(initialDAirplane.wing.span, "m", "ft")))
print("chord:                   {:.3f} ft".format(convert(initialDAirplane.wing.chord, "m", "ft")))
print("horizontal stabilizer")
print("span:                    {:.3f} ft".format(convert(initialDAirplane.horizontalStabilizer.span, "m", "ft")))
print("chord:                   {:.3f} ft".format(convert(initialDAirplane.horizontalStabilizer.chord, "m", "ft")))
print("vertical stabilizer")
print("span:                    {:.3f} ft".format(convert(initialDAirplane.verticalStabilizer.span, "m", "ft")))
print("chord:                   {:.3f} ft".format(convert(initialDAirplane.verticalStabilizer.chord, "m", "ft")))

print("---- Weight & Balance")
for c in initialDAirplane.components:
    print("weight: {:10.3f} lb - position {:10.3f} ft - {}".format(convert(c.mass*g, "N", "lb"), convert(c.x, "m", "ft"), type(c)))

simulation = designDict["simulation"]
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
title("Design Mission Track")

figure()
plot([convert(t, "s", "hr") for t in ts], [convert(V, "m/s", "kts") for V in Vs])
xlabel("Time [hr]")
ylabel("Speed [kts]")
title("Design Mission Velocity Track")

figure()
plot([convert(CG, "m", "ft") for CG in CGs], [convert(W, "N", "lb") for W in Ws])
xlabel("C.G. [ft]")
ylabel("Weight [lb]")
title("Design Mission C.G. Movement")

simulation = referenceDict["simulation"]
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
title("Reference Mission Track")

figure()
plot([convert(t, "s", "hr") for t in ts], [convert(V, "m/s", "kts") for V in Vs])
xlabel("Time [hr]")
ylabel("Speed [kts]")
title("Reference Mission Velocity Track")

figure()
plot([convert(CG, "m", "ft") for CG in CGs], [convert(W, "N", "lb") for W in Ws])
xlabel("C.G. [ft]")
ylabel("Weight [lb]")
title("Reference Mission C.G. Movement")

simulation = abortedDict["simulation"]
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
title("Aborted Mission Track")

show()
