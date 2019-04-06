import sys
import os
sys.path.append(os.path.join(sys.path[0], ".."))

from constants import *
from parameters import *

import copy

################################################################################
# AIRPLANE DEFINITION
################################################################################

airfoil = Airfoil(os.path.join(sys.path[0], "data", "SF1.csv"))
wing = Wing(1, convert(40*5, "ft^2", "m^2"), 0.02, convert(40, "ft", "m"))
wing.maximumLiftCoefficient = 2
wing.airfoil = airfoil
gas = Gas()
gas.energyDensity = avgasEnergyDensity
gas.density = avgasDensity
gas.mass = convert(50, "gal", "m^3")*gas.density
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
engineNacelle = Nacelle(1, convert(1.5, "ft", "m"), convert(4, "ft", "m"))
engine = Engine()
engine.maxPower = convert(130, "hp", "W")
engine.propeller = propeller
engine.nacelle = engineNacelle
engineL = engine
engineR = copy.deepcopy(engine)
fuselage = Fuselage(1, convert(7, "ft", "m"), convert(30, "ft", "m"))
horizontalStabilizer = Surface(1.2, convert(10*3, "ft^2", "m^2"), 0.12, convert(10, "ft", "m"))
verticalStabilizer = Surface(1.1, convert(6*3, "ft^2", "m^2"), 0.12, convert(6, "ft", "m"))
tail = Tail()
tail.horizontalStabilizer = horizontalStabilizer
tail.verticalStabilizer = verticalStabilizer
# landingGear # TODO: add to components of airplane

airplane = Airplane()
airplane.name = "testcraft"
airplane.altitude = 0
airplane.position = 0
airplane.speed = 0
airplane.throttle = 0
airplane.pilots = 1
airplane.passengers = 3
airplane.flightPathAngle = 0
airplane.pitch = 0 # pitch angle of airplane (where the nose is pointing)
airplane.wing = wing
airplane.tail = tail
airplane.powerplant = powerplant
airplane.engines = [engineL, engineR] # [engine object] # list of engines on airplane
airplane.components = [wing, engineL.nacelle, engineR.nacelle, fuselage, horizontalStabilizer, verticalStabilizer] # [component objects] # list of components making up airplane (including parts used elsewhere)
airplane.oswaldEfficiencyFactor = 0.8
airplane.compressibilityDragCoefficient = 0
airplane.miscellaneousParasiteDragFactor = 0.004 # FIXME: ?
airplane.initialGrossWeight = convert(4000, "lb", "N")