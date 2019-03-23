import sys
sys.path.insert(0, sys.path[0] + "/../")
from convert import convert # unit conversions
from stdatmo import * # standard atmospheric conditions
from scipy import * # math
from matplotlib.pyplot import * # plotting

from parameters import *
from constants import *
from equations import *

################################################################################
# AIRPLANE DEFINITION
################################################################################

wing = Wing(1, convert(40*5, "ft^2", "m^2"), 0.02, convert(40, "ft", "m"))
propeller = Propeller()
diameter = convert(6, "ft", "m")
angularVelocity = 0
efficiency = 0.9
engine = Engine()
engine.maxPower = None # number [W] : (0 <= x)
engine.propeller = None # propeller object
engineL = engine
engineR = deepcopy(engine)

airplane = Airplane()
airplane.altitude = 0
airplane.position = 0
airplane.speed = 0
airplane.throttle = 0
airplane.pilots = 1
airplane.passengers = 3
airplane.flightPathAngle = 0
airplane.wing = wing
airplane.engines = [engineL, engineR] # [engine object] # list of engines on airplane
airplane.components = [wing, engineL, engineR] # [component objects] # list of components making up airplane (including wing)
airplane.oswaldEfficiencyFactor = 0.8
airplane.compressibilityDrag = 0
airplane.miscellaneousParasiteDragFactor = 0.02 # FIXME: ?

################################################################################
# EVALUATION
################################################################################

