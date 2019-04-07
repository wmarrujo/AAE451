import sys
import os
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
airplane = Airplane()
airplane.InitialGrossWeight = convert(4500, "lb", "N") # [N]
airplane.LoadFactor = 3.5 # FIXME what load factor do we size with for a twin engine GA aricraft? 3?

gas = Gas()
gas.mass = convert(400, "lb", "N")/g
gas.energyDensity = avgasEnergyDensity
gas.density = avgasDensity

powerplant = Powerplant()
powerplant.gas = gas
powerplant.battery = None
powerplant.generator = None
powerplant.percentElectric = 0
powerplant.generatorOn = False
airplane.powerplant = powerplant

############### MAIN WING INPUT AREA ###############
airfoil = Airfoil(os.path.join(sys.path[0], "data", "SF1.csv"))
wing = Wing(1, convert(40*5, "ft^2", "m^2"), 0.02, convert(40, "ft", "m"), 0, 1, airplane)
wing.maximumLiftCoefficient = 2
wing.airfoil = airfoil
airplane.wing = wing

############### FUSELAGE INPUT AREA ###############
fuselage = Fuselage(1, convert(7, "ft", "m"), convert(30, "ft", "m"), airplane)
airplane.fuselage = fuselage

############### STABILIZERS INPUT AREA ###############
horizontalStabilizer = HorizontalStabilizer(1.2, convert(10*3, "ft^2", "m^2"), 0.12, convert(10, "ft", "m"), 0, 1, airplane)
verticalStabilizer = VerticalStabilizer(1.1, convert(6*3, "ft^2", "m^2"), 0.12, convert(6, "ft", "m"), 0, 1, airplane)
tail = Tail()
tail.horizontalStabilizer = horizontalStabilizer
tail.verticalStabilizer = verticalStabilizer
airplane.tail = tail


############### PROPELLER INPUT AREA ###############
propeller = Propeller()
propeller.diameter = convert(6, "ft", "m")
propeller.angularVelocity = 0
propeller.efficiency = 0.9

############### ENGINE INPUT AREA ###############
engine = Engine(1, convert(1.5, "ft", "m"), convert(4, "ft", "m"), 98, 2)
engine.maxPower = convert(130, "hp", "W")
engine.propeller = propeller
engineL = engine
engineR = copy.deepcopy(engine)
airplane.engines = [engineL, engineR] # [engine object] # list of engines on airplane

############### LANDING GEAR INPUT AREA ###############
NLand = airplane.LoadFactor * 1.5 # Ultimate Load Factor
mainGear = MainGear(NLand, convert(1, "m", "ft"), airplane)# First input = LandingLoadFactor, Second input = lengthMainGear (m)
frontGear = FrontGear(NLand, convert(1, "m", "ft"), airplane) # First input = LandingLoadFactor, Second input = lengthFrontGear (m)

############### MISCELLANEOUS COMPONENT INPUT AREA ###############
fuelSystem = FuelSystem(airplane)
airplane.fuelSystem = fuelSystem
flightControls = FlightControls(airplane)
airplane.flightControls = flightControls
hydraulics = Hydraulics(airplane)
airplane.hydraulics = hydraulics
avionics = Avionics(4000) # INPUT = uninstalled avioncs weight [N] (typically 800-1400 lb or 3558 - 6227 N)
airplane.avionics = avionics
electronics = Electronics(airplane)
airplane.electronics = electronics
airplane.pilots = 1
airplane.passengers = 3
airconIce = AirConIce(airplane) # Airconditioning and Anti Ice
airplane.airconIce = airconIce
furnishings = Furnishings(airplane)
airplane.furnishings = furnishings

airplane.components = [wing, engineL, engineR, fuselage, horizontalStabilizer, verticalStabilizer, mainGear, frontGear, fuelSystem, hydraulics, flightControls, avionics, electronics, airconIce, furnishings] # [component objects] # list of components making up airplane (including parts used elsewhere)

airplane.oswaldEfficiencyFactor = 0.8
airplane.compressibilityDragCoefficient = 0
airplane.miscellaneousParasiteDragFactor = 0.004 # FIXME: ?
airplane.emptyWeight = sum([component.mass for component in airplane.components]) # TODO: will be replaced with component weight buildup

airplane.altitude = 0
airplane.position = 0
airplane.speed = 0
airplane.throttle = 0
airplane.flightPathAngle = 0
airplane.pitch = 0 # pitch angle of airplane (where the nose is pointing)

################################################################################
# EVALUATION
################################################################################

simulation = {"time":[], "segment":[], "weight":[], "position":[], "altitude":[], "speed":[], "pitch":[], "flightPathAngle":[]}
def recordingFunction(t, segmentName, airplane):
    print("{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f} {segment} | W:{weight:5.0f} lbs - x:{position:5.0f} nmi - h:{altitude:5.0f} ft - V:{speed:5.0f} kts - p:{pitch:5.0f} deg - fpa:{flightPathAngle:5.0} deg".format(
        hours=floor(t/(60*60)),
        minutes=floor(t/60)%60,
        seconds=t%60,
        segment=segmentName,
        weight=convert(AirplaneWeight(airplane), "N", "lb"),
        position=convert(airplane.position, "m", "nmi"),
        altitude=convert(airplane.altitude, "m", "ft"),
        speed=convert(airplane.speed, "m/s", "kts"),
        pitch=convert(airplane.pitch, "rad", "deg"),
        flightPathAngle=convert(airplane.flightPathAngle, "rad", "deg")))
    
    simulation["time"] += [t]
    simulation["segment"] += [segmentName]
    simulation["weight"] += [AirplaneWeight(airplane)]
    simulation["position"] += [airplane.position]
    simulation["altitude"] += [airplane.altitude]
    simulation["speed"] += [airplane.speed]
    simulation["pitch"] += [airplane.pitch]
    simulation["flightPathAngle"] += [airplane.flightPathAngle]

# designMission.simulate(1, airplane, recordingFunction)
# dictToCSV("./data/testSimulation.csv", simulation)
#
# ts_min = [convert(t, "s", "min") for t in simulation["time"]]
# hs_ft = [convert(h, "m", "ft") for h in simulation["altitude"]]
# xs_ft = [convert(x, "m", "ft") for x in simulation["position"]]
# xs_nmi = [convert(x, "m", "nmi") for x in simulation["position"]]
# ps_deg = [convert(p, "rad", "deg") for p in simulation["pitch"]]
# fpas_deg = [convert(a, "rad", "deg") for a in simulation["flightPathAngle"]]
# aoas_deg = [p - fpa for (p, fpa) in zip(ps_deg, fpas_deg)]
# 
# figure()
# plot(xs_nmi, hs_ft)
# title("Track")
# xlabel("position [nmi]")
# ylabel("altitude [ft]")
# 
# figure()
# plot(ts_min, xs_nmi)
# title("Range History")
# xlabel("time [min]")
# ylabel("position [nmi]")
# 
# figure()
# plot(ts_min, hs_ft)
# title("Altitude History")
# xlabel("time [min]")
# ylabel("altitude [ft]")
# 
# figure()
# plot(ts_min, ps_deg, label="pitch")
# plot(ts_min, fpas_deg, label="flight path angle")
# plot(ts_min, aoas_deg, label="angle of Attack")
# title("Angle History")
# xlabel("time [min]")
# ylabel("angle [deg]")
# legend()

# DEBUG: Drag buildup

Vs = [convert(v, "kts", "m/s") for v in range(0, 300)]
As = [copy.copy(airplane) for v in Vs]
for i, (A, V) in enumerate(zip(As, Vs)):
    A.speed = V
    As[i] = A
qs = [AirplaneDynamicPressure(A) for A in As]
Ls = [AirplaneLift(A) for A in As]
Ds = [AirplaneDrag(A) for A in As]
CLs = [LiftCoefficient(A) for A in As]
CDs = [DragCoefficient(A) for A in As]
CD0s = [ParasiteDragCoefficient(A) for A in As]
CDis = [InducedDragCoefficient(A) for A in As]

figure()
plot(Vs, Ls, label="L")
plot(Vs, Ds, label="D")
legend()

figure()
plot(Vs, CLs, label="CL")
plot(Vs, CDs, label="CD")
plot(Vs, CD0s, label="CD0")
plot(Vs, CDis, label="CDi")
legend()

show()
