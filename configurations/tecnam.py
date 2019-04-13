import sys
import os
root = os.path.join(sys.path[0], "..")
sys.path.append(root)

from constants import *
from parameters import *

import copy

################################################################################
# AIRPLANE INITIALIZATION
################################################################################

airplane = Airplane()
airplane.name = "testcraft"
airplane.InitialGrossWeight = convert(2712, "lb", "N") # [N]

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
gas.mass = 144 #convert(50, "gal", "m^3")*gas.density ##

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

airfoil = Airfoil(os.path.join(root, "data", "SF1.csv"))
wing = Wing(1, 14.78, 0.02, 11.4, 0, 1, airplane) #interferenceFactor, planformArea, thicknessToChord, span, sweep, taper, airplane
wing.maximumLiftCoefficient = 2
wing.airfoil = airfoil
airplane.wing = wing

################################################################################
# FUSELAGE DEFINITION
################################################################################

fuselage = Fuselage(1, 1.4, 8.7, airplane) #interferenceFactor, diameter, length, airplane
airplane.fuselage = fuselage

################################################################################
# TAIL DEFINITION
################################################################################

horizontalStabilizer = HorizontalStabilizer(1.2, 2.64, 0.12, convert(10, "ft", "m"), 0 , 1, airplane) #interferenceFactor, planformArea, thicknessToChord, span, sweep, taper, airplane
verticalStabilizer = VerticalStabilizer(1.1, 2.86, 0.12, convert(6, "ft", "m"), deg2rad(20), 1, airplane)
airplane.horizontalStabilizer = horizontalStabilizer
airplane.verticalStabilizer = verticalStabilizer

################################################################################
# PROPELLER DEFINITION
################################################################################

propeller = Propeller()
propeller.diameter = 1.65
propeller.angularVelocity = 0
propeller.efficiency = 0.9

################################################################################
# ENGINE DEFINITION
################################################################################

engine = Engine(1, 0.65, 1.8, 65.7, 2) #interferenceFactor, diameter, length, uninstalledMass, numberOfEngines
engine.maxPower = convert(98.6, "hp", "W")
engine.propeller = propeller
engineL = engine
engineR = copy.deepcopy(engine)
airplane.engines = [engineL, engineR] # [engine object] # list of engines on airplane

################################################################################
# LANDING GEAR DEFINITION
################################################################################

NLand = 2.67 * 1.5 # Ultimate Landing Load Factor = gear load factor (14 CFR 23) * 1.5
mainGear = MainGear(NLand, .5, airplane) # First input = LandingLoadFactor, Second input = lengthMainGear (m)
frontGear = FrontGear(NLand, .5, airplane) # First input = LandingLoadFactor, Second input = lengthFrontGear (m)

################################################################################
# MISCELLANEOUS COMPONENT DEFINITIONS
################################################################################

fuelSystem = FuelSystem(airplane)
airplane.fuelSystem = fuelSystem
flightControls = FlightControls(airplane)
airplane.flightControls = flightControls
hydraulics = Hydraulics(airplane)
airplane.hydraulics = hydraulics
avionics = Avionics(4*9.8) # INPUT = uninstalled avioncs weight [N] (typically 800-1400 lb or 3558 - 6227 N) WHAT THE SHIT # 78 kg?
airplane.avionics = avionics
electronics = Electronics(airplane)
airplane.electronics = electronics
airplane.pilots = 1
airplane.passengers = 3
airconIce = AirConIce(airplane) # Airconditioning and Anti Ice
airplane.airconIce = airconIce
furnishings = Furnishings(airplane)
airplane.furnishings = furnishings

################################################################################
# AIRPLANE FINALIZATION
################################################################################

airplane.components = [wing, engineL, engineR, fuselage, horizontalStabilizer, verticalStabilizer, mainGear, frontGear, fuelSystem, hydraulics, flightControls, avionics, electronics, airconIce, furnishings] # [component objects] # list of components making up airplane (including parts used elsewhere)
emptymass = sum([thing.mass for thing in airplane.components])

print('wing = ', wing.mass, ' kg')
print('engineL = ', engineL.mass, ' kg')
print('engineR = ', engineR.mass, ' kg')
print('fuselage = ', fuselage.mass, ' kg')
print('horizontalstabilizer = ', horizontalStabilizer.mass, ' kg')
print('verticalStabilizer = ', verticalStabilizer.mass, ' kg')
print('mainGear = ', mainGear.mass, ' kg')
print('frontGear = ', frontGear.mass, ' kg')
print('fuelSystem = ', fuelSystem.mass, ' kg')
print('hydraulics = ', hydraulics.mass, ' kg')
print('flightControls = ', flightControls.mass, ' kg')
print('avionics = ', avionics.mass, ' kg')
print('electronics = ', electronics.mass, ' kg')
print('airconIce = ', airconIce.mass, ' kg')
print('furnishings = ', furnishings.mass, ' kg')

print('We = ',emptymass,' kg')

airplane.oswaldEfficiencyFactor = 0.8
airplane.compressibilityDragCoefficient = 0
airplane.miscellaneousParasiteDragFactor = 0.004 # FIXME: what should this be?
