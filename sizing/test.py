import sys
sys.path.insert(0, sys.path[0] + "/../")
from convert import convert # unit conversions
from stdatmo import * # standard atmospheric conditions
from scipy import * # math
from matplotlib.pyplot import * # plotting
import copy

from constants import *
from parameters import *
from equations import *
from missions import *

################################################################################
# AIRPLANE DEFINITION
################################################################################

airfoil = Airfoil("./data/SF1.csv")
wing = Wing(1, convert(40*5, "ft^2", "m^2"), 0.02, convert(40, "ft", "m"))
wing.maximumLiftCoefficient = 2
wing.airfoil = airfoil
gas = Gas()
gas.mass = convert(400, "lb", "N")/g
gas.energyDensity = avgasEnergyDensity
powerplant = Powerplant()
powerplant.gas = gas
powerplant.battery = None
powerplant.generator = None
powerplant.percentElectric = 0
powerplant.generatorOn = False
propeller = Propeller()
propeller.diameter = convert(6, "ft", "m")
propeller.angularVelocity = 0
propeller.efficiency = 0.9
engine = Engine()
engine.maxPower = convert(130, "hp", "W")
engine.propeller = propeller
engineL = engine
engineR = copy.deepcopy(engine)

airplane = Airplane()
airplane.altitude = 0
airplane.position = 0
airplane.speed = 0
airplane.throttle = 0
airplane.pilots = 1
airplane.passengers = 3
airplane.flightPathAngle = 0
airplane.pitch = 0 # pitch angle of airplane (where the nose is pointing)
airplane.wing = wing
airplane.powerplant = powerplant
airplane.engines = [engineL, engineR] # [engine object] # list of engines on airplane
airplane.components = [wing] # [component objects] # list of components making up airplane (including wing)
airplane.oswaldEfficiencyFactor = 0.8
airplane.compressibilityDragCoefficient = 0
airplane.miscellaneousParasiteDragFactor = 0.004 # FIXME: ?
airplane.emptyWeight = convert(4000, "lb", "N") # TODO: will be replaced with component weight buildup

################################################################################
# EVALUATION
################################################################################

simulation = {"time":[], "segment":[], "weight":[], "position":[], "altitude":[], "speed":[], "pitch":[], "flightPathAngle":[]}
def recordingFunction(t, segmentName, airplane):
    # print("{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f} {segment} | W:{weight:5.0f} lbs - x:{position:5.0f} ft - h:{altitude:5.0f} ft - V:{speed:5.0f} kts - p:{pitch:5.0f} deg - fpa:{flightPathAngle:5.0} deg".format(
    #     hours=floor(t/(60*60)),
    #     minutes=floor(t/60)%60,
    #     seconds=t%60,
    #     segment=segmentName,
    #     weight=convert(AirplaneWeight(airplane), "N", "lb"),
    #     position=convert(airplane.position, "m", "ft"),
    #     altitude=convert(airplane.altitude, "m", "ft"),
    #     speed=convert(airplane.speed, "m/s", "kts"),
    #     pitch=convert(airplane.pitch, "rad", "deg"),
    #     flightPathAngle=convert(airplane.flightPathAngle, "rad", "deg")))
    
    simulation["time"] += [t]
    simulation["segment"] += [segmentName]
    simulation["weight"] += [AirplaneWeight(airplane)]
    simulation["position"] += [airplane.position]
    simulation["altitude"] += [airplane.altitude]
    simulation["speed"] += [airplane.speed]
    simulation["pitch"] += [airplane.pitch]
    simulation["flightPathAngle"] += [airplane.flightPathAngle]

designMission.simulate(1, airplane, recordingFunction)
dictToCSV("./data/testSimulation.csv", simulation)

ts_min = [convert(t, "s", "min") for t in simulation["time"]]
hs_ft = [convert(h, "m", "ft") for h in simulation["altitude"]]
xs_nmi = [convert(x, "m", "nmi") for x in simulation["position"]]

figure(1)
plot(ts_min, xs_nmi)
title("Range")
xlabel("time [min]")
ylabel("position [nmi]")

figure(2)
plot(ts_min, hs_ft)
title("Altitude")
xlabel("time [min]")
ylabel("altitude [ft]")

figure(3)
plot(xs_nmi, hs_ft)
title("Track")
xlabel("position [ft]")
ylabel("altitude [nmi]")

show()