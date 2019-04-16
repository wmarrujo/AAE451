import sys
import os
sys.path.append(os.path.join(sys.path[0], ".."))

from constants import *
from parameters import *

import copy

################################################################################
# AIRPLANE INITIALIZATION
################################################################################

airplane = Airplane()
airplane.name = "testcraft"
airplane.InitialGrossWeight = convert(4500, "lb", "N") # [N]

airplane.altitude = 0
airplane.position = 0
airplane.speed = 0
airplane.throttle = 0
airplane.flightPathAngle = 0
airplane.pitch = 0 # pitch angle of airplane (where the nose is pointing)
airplane.LoadFactor = 3.5 # FIXME what load factor do we size with for a twin engine GA aricraft? 3?

################################################################################
# POWERPLANT DEFINITION
################################################################################

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
airplane.powerplant = powerplant

################################################################################
# WING DEFINITION
################################################################################

airfoil = Airfoil(os.path.join(sys.path[0], "data", "SF1.csv"))
wing = Wing(1, convert(40*5, "ft^2", "m^2"), 0.02, convert(40, "ft", "m"), 0, 1, airplane)
wing.maximumLiftCoefficient = 2
# wing.minimumDragCoefficient = 0.024
wing.airfoil = airfoil
airplane.wing = wing

################################################################################
# FUSELAGE DEFINITION
################################################################################

fuselage = Fuselage(1, convert(7, "ft", "m"), convert(30, "ft", "m"), airplane)
airplane.fuselage = fuselage

################################################################################
# TAIL DEFINITION
################################################################################

horizontalStabilizer = HorizontalStabilizer(1.2, convert(10*3, "ft^2", "m^2"), 0.12, convert(10, "ft", "m"), 0, 1, airplane)
verticalStabilizer = VerticalStabilizer(1.1, convert(6*3, "ft^2", "m^2"), 0.12, convert(6, "ft", "m"), 0, 1, airplane)
airplane.horizontalStabilizer = horizontalStabilizer
airplane.verticalStabilizer = verticalStabilizer

################################################################################
# PROPELLER DEFINITION
################################################################################

propeller = Propeller()
propeller.diameter = convert(6, "ft", "m")
propeller.angularVelocity = 0
propeller.efficiency = 0.8

################################################################################
# ENGINE DEFINITION
################################################################################

engine = Engine(1, convert(1.5, "ft", "m"), convert(4, "ft", "m"), 98, 2)
engine.maxPower = convert(165, "hp", "W")
engine.propeller = propeller
engineL = engine
engineR = copy.deepcopy(engine)
airplane.engines = [engineL, engineR] # [engine object] # list of engines on airplane

################################################################################
# LANDING GEAR DEFINITION
################################################################################

NLand = airplane.LoadFactor * 1.5 # Ultimate Load Factor
mainGear = MainGear(NLand, 1, airplane) # First input = LandingLoadFactor, Second input = lengthMainGear (m)
frontGear = FrontGear(NLand, 1, airplane) # First input = LandingLoadFactor, Second input = lengthFrontGear (m)
airplane.retractableGear = True  ##### Sarah's change

################################################################################
# MISCELLANEOUS COMPONENT DEFINITIONS
################################################################################

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
airplane.passengers = 5
airconIce = AirConIce(airplane) # Airconditioning and Anti Ice
airplane.airconIce = airconIce
furnishings = Furnishings(airplane)
airplane.furnishings = furnishings
airplane.compositeFraction = 1 ##### Sarah's change

################################################################################
# AIRPLANE FINALIZATION
################################################################################

airplane.components = [wing, engineL, engineR, fuselage, horizontalStabilizer, verticalStabilizer, mainGear, frontGear, fuelSystem, hydraulics, flightControls, avionics, electronics, airconIce, furnishings] # [component objects] # list of components making up airplane (including parts used elsewhere)

airplane.oswaldEfficiencyFactor = 0.8
airplane.compressibilityDragCoefficient = 0
airplane.miscellaneousParasiteDragFactor = 0.004 # FIXME: what should this be?
