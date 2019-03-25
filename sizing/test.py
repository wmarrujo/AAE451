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
airplane.wing = wing
airplane.powerplant = powerplant
airplane.engines = [engineL, engineR] # [engine object] # list of engines on airplane
airplane.components = [wing] # [component objects] # list of components making up airplane (including wing)
airplane.oswaldEfficiencyFactor = 0.8
airplane.compressibilityDrag = 0
airplane.miscellaneousParasiteDragFactor = 0.004 # FIXME: ?
airplane.emptyWeight = convert(4000, "lb", "N") # TODO: will be replaced with component weight buildup
airplane.angleOfAttack = 0

################################################################################
# EVALUATION
################################################################################

def recordingFunction(t, segmentName, airplane):
    print("{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f} {segment} | W:{weight:5.0f} lbs - x:{position:5.0f} ft - h:{altitude:5.0f} ft - V:{speed:5.0f} kts".format(
        hours=floor(t/(60*60)),
        minutes=floor(t/60)%60,
        seconds=t%60,
        segment=segmentName,
        weight=convert(AirplaneWeight(airplane), "N", "lb"),
        position=convert(airplane.position, "m", "ft"),
        altitude=convert(airplane.altitude, "m", "ft"),
        speed=convert(airplane.speed, "m/s", "kts")))

designMission.simulate(1, airplane, recordingFunction)