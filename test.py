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


# DEBUG: testing that defineAirplane works

DPS = [convert(50, "lb/ft^2", "N/m^2"), convert(0.072, "hp/lb", "W/N")]

airplane = defineAirplane(DPS, testcraft)

Wi = airplane.initialGrossWeight
W0 = AirplaneWeight(airplane)
We = EmptyWeight(airplane)
Wpay = PayloadWeight(airplane)
WF = FuelWeight(airplane)

print("Wi: {:.0f} lb - W0:  {:.0f} lb - We: {:.0f} lb - Wpay: {:.0f} lb - WF: {:.0f} lb".format(
    convert(Wi, "N", "lb"),
    convert(W0, "N", "lb"),
    convert(We, "N", "lb"),
    convert(Wpay, "N", "lb"),
    convert(WF, "N", "lb")))

# DEBUG: Testing that airplane runs

# WS = convert(17, "lb/ft^2", "N/m^2")
# PW = convert(0.072, "hp/lb", "W/N")
# 
# testcraft.initialGrossWeight = convert(3500, "lb", "N")
# 
# def defineAirplaneWithX(A, X):
#     B = copy.deepcopy(A)
#     S = B.wing.planformArea
#     Engines = B.engines
#     W0 = X[0] # initial gross weight
#     We = EmptyWeight(A)
#     Wpay = PayloadWeight(A)
# 
#     S = W0 / WS
#     Wf = W0 - We - Wpay
#     B.initialGrossWeight = W0
#     B.powerplant.fuelMass = Wf/g # put on just enough fuel to get through mission
#     B.wing.setPlanformAreaWhileMaintainingAspectRatio(S)
#     for engine in Engines:
#         engine.maxPower = PW/len(Engines) * W0 # TODO: assuming all engines are the same size, change to each proportionally if needed
# 
#     print(A.initialGrossWeight, AirplaneWeight(A), A.powerplant.fuelMass, A.wing.planformArea, S)
#     print(B.initialGrossWeight, AirplaneWeight(B), B.powerplant.fuelMass, B.wing.planformArea, S)
# 
#     return B
# 
# # airplane = defineAirplaneWithX(testcraft, [convert(3500, "lb", "N")])
# gwguesses = [convert(gwguess, "lb", "N") for gwguess in linspace(1000, 4000, 15)]
# airplanes = [defineAirplaneWithX(testcraft, [gwguess]) for gwguess in gwguesses]
# fuelWeights = []
# for airplane in airplanes:
#     designMission.simulate(1, airplane)
#     fuelWeights.append(abs(FuelWeight(airplane)))
# 
# figure()
# plot(gwguesses, fuelWeights)
# 
# show()

# DEBUG: simulation

# simulation = {"time":[], "segment":[], "x":[], "h":[], "g":[], "p":[], "v":[]}
# def recordSimulation(t, s, a):
#     simulation["time"].append(t)
#     simulation["segment"].append(s)
#     simulation["x"].append(a.position)
#     simulation["h"].append(a.altitude)
#     simulation["g"].append(a.flightPathAngle)
#     simulation["p"].append(a.pitch)
#     simulation["v"].append(a.speed)
#
# W0 = AirplaneWeight(airplane)
# Wf = FuelWeight(airplane)
# We = EmptyWeight(airplane)
# Wpay = PayloadWeight(airplane)
#
#
# success = designMission.simulate(1, airplane, recordSimulation)
#
#
# print("Mission Finished" if success else "Mission Failed")
# print("W0i: {:.0f} lb - W0: {:.0f} lb - Wf: {:.0f} lb - WFi: {:.0f} lb - WFf: {:.0f} lb - We: {:.0f} lb - Wpay: {:.0f} lb".format(
#     convert(airplane.initialGrossWeight, "N", "lb"),
#     convert(W0, "N", "lb"),
#     convert(AirplaneWeight(airplane), "N", "lb"),
#     convert(Wf, "N", "lb"),
#     convert(FuelWeight(airplane), "N", "lb"),
#     convert(We, "N", "lb"),
#     convert(Wpay, "N", "lb")))
#
# ts_hr = [convert(t, "s", "hr") for t in simulation["time"]]
# xs_nmi = [convert(x, "m", "nmi") for x in simulation["x"]]
# hs_ft = [convert(h, "m", "ft") for h in simulation["h"]]
# vs_kts = [convert(v, "m/s", "kts") for v in simulation["v"]]
# ps_deg = [convert(p, "rad", "deg") for p in simulation["p"]]
# gs_deg = [convert(g, "rad", "deg") for g in simulation["g"]]
#
# figure()
# plot(xs_nmi, hs_ft, "k-")
# title("Track")
#
# figure()
# plot(ts_hr, hs_ft, "k-")
# title("Altitude History")
#
# figure()
# plot(ts_hr, ps_deg, "r-", label="pitch")
# plot(ts_hr, gs_deg, "k-", label="gamma")
# title("Angle History")
# legend()
#
# figure()
# plot(ts_hr, vs_kts, "k-")
# title("Velocity History")
#
# show()
