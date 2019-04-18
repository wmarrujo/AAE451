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
from equations import *

# EXTERNAL DEPENDENCIES

import copy

################################################################################

def defineAirplane(definingParameters):
    ################################################################################
    # GET DEFINING PARAMETERS
    ################################################################################
    
    W0 = definingParameters["initial gross weight"]
    Wf = definingParameters["initial fuel weight"]
    WS = definingParameters["wing loading"]
    PW = definingParameters["power to weight ratio"]
    
    # ASSUMPTIONS # FIXME: Define elsewhere? or get from simulations?
    cruiseDynamicPressure = 0.5*densityAtAltitude(cruiseAltitude)*convert(180, "kts", "m/s")**2
    sizingLoadFactor = 3.5
    landingLoadFactor = sizingLoadFactor * 1.5
    horizontalTailVolumeCoefficient = 0.80
    verticalTailVolumeCoefficient = 0.07
    numberOfEngines = 2
    uninstalledEngineMass = 98 # kg
    totalFuelVolume = convert(50, "gal", "m^3")
    uninstalledAvionicsWeight = 4000 # N
    cruiseMachNumber = convert(180, "kts", "m/s") / machAtAltitude(cruiseAltitude)
    
    ################################################################################
    # 0: AIRPLANE OBJECT INITIALIZATION
    ################################################################################
    
    airplane = Airplane()
    
    airplane.initialGrossWeight = W0
    airplane.pilots = 1
    airplane.passengers = 5
    airplane.oswaldEfficiencyFactor = 0.8
    airplane.compressibilityDragCoefficient = 0
    airplane.miscellaneousParasiteDragFactor = 0.004 # FIXME: what should this be?
    airplane.components = []
    
    ################################################################################
    # 1: POWERPLANT DEFINITION
    ################################################################################
    
    # GAS OBJECT DEFINITION
    
    gas = Gas()
    
    gas.energyDensity = avgasEnergyDensity
    gas.density = avgasDensity
    gas.x = 4 # m
    
    # POWERPLANT OBJECT DEFINITION
    
    powerplant = Powerplant()
    
    powerplant.gas = gas
    powerplant.percentElectric = 0
    powerplant.fuelMass = Wf/g
    powerplant.generatorOn = True
    
    generator = Generator()
    generator.efficiency = 0.4
    generator.power = convert(160, "hp", "W")
    generator.x = convert(2.2,"ft","m")
    
    
    
    # FINISH AIRPLANE DEFINITION FOR THIS SECTION
    powerplant.generator = generator
    airplane.powerplant = powerplant
    
    ################################################################################
    # 2: WING DEFINITION
    ################################################################################
    
    # AIRFOIL OBJECT
    
    airfoil = Airfoil(os.path.join(rootDirectory, "data", "SF1.csv"))
    
    # WING OBJECT
    
    wing = Wing()
    
    wing.airfoil = airfoil
    wing.interferenceFactor = 1
    wing.planformArea = W0/WS
    wing.setAspectRatioHoldingPlanformArea(8.7)
    wing.thicknessToChord = 0.02
    wing.sweep = 0
    wing.taperRatio = 1
    wing.mass = PredictWingMass(wing.span, wing.aspectRatio, wing.chord, 3.5, wing.sweep, wing.taperRatio, wing.planformArea, airplane.initialGrossWeight, powerplant.fuelMass*g, cruiseDynamicPressure, wing.thicknessToChord)
    wing.x = convert(11.75,"ft","m")
    
    # FINISH AIRPLANE DEFINITION FOR THIS SECTION
    
    airplane.wing = wing
    airplane.components += [wing]
    
    ################################################################################
    # 3: FUSELAGE DEFINITION
    ################################################################################
    
    # FUSELAGE OBJECT
    
    fuselage = Fuselage()
    
    fuselage.interferenceFactor = 1
    fuselage.diameter = convert(6, "ft", "m")
    fuselage.length = convert(30, "ft", "m")
    fuselage.mass = PredictFuselageMass(fuselage.wettedArea, airplane.initialGrossWeight, 0.45*fuselage.length, fuselage.diameter, cruiseDynamicPressure, 0, 3.5)
    fuselage.x = convert(fuselage.length/2,"ft","m")
    
    # FINISH AIRPLANE DEFINITION FOR THIS SECTION
    
    airplane.fuselage = fuselage
    airplane.components += [fuselage]
    
    ################################################################################
    # 4: TAIL DEFINITION
    ################################################################################
    
    # HORIZONTAL STABILIZER OBJECT
    
    horizontalStabilizer = HorizontalStabilizer()
    horizontalStabilizer.interferenceFactor = 1.2
    horizontalStabilizer.planformArea = convert(25, "ft^2", "m^2")
    horizontalStabilizer.thicknessToChord = 0.12
    horizontalStabilizer.span = convert(10, "ft", "m")
    horizontalStabilizer.sweep = 0
    horizontalStabilizer.taperRatio = 1
    horizontalStabilizer.mass = PredictHorizontalStabilizerMass(airplane.initialGrossWeight, sizingLoadFactor, horizontalStabilizer.taperRatio, horizontalStabilizer.sweep, wing.taperRatio, horizontalTailVolumeCoefficient, wing.span, wing.chord, 0.5 * fuselage.length, cruiseDynamicPressure, wing.thicknessToChord)
    horizontalStabilizer.x = convert(27.5,"ft","m")
    
    # VERTICAL STABILIZER OBJECT
    
    verticalStabilizer = VerticalStabilizer()
    verticalStabilizer.interferenceFactor = 1.1
    verticalStabilizer.planformArea = convert(37, "ft^2", "m^2")
    verticalStabilizer.thicknessToChord = 0.12
    verticalStabilizer.span = convert(9.9, "ft", "m")
    verticalStabilizer.sweep = 0
    verticalStabilizer.taperRatio = 1
    verticalStabilizer.mass = PredictVerticalStabilizerMass(verticalStabilizer.taperRatio, verticalStabilizer.sweep, sizingLoadFactor, 1, airplane.initialGrossWeight, cruiseDynamicPressure, verticalTailVolumeCoefficient, 0.5 * fuselage.length, wing.span, wing.chord, wing.planformArea, wing.thicknessToChord)
    verticalStabilizer.x = convert(26.1,"ft","m")
    # FINISH AIRPLANE DEFINITION FOR THIS SECTION
    
    airplane.horizontalStabilizer = horizontalStabilizer
    airplane.verticalStabilizer = verticalStabilizer
    airplane.components += [horizontalStabilizer, verticalStabilizer]
    
    ################################################################################
    # 5: ENGINE DEFINITION
    ################################################################################
    
    # PROPELLER OBJECT
    
    propeller = Propeller()
    
    propeller.diameter = convert(6.25, "ft", "m")
    propeller.efficiency = 0.9
    
    # ENGINE OBJECT
    
    engine = Engine()
    
    engine.interferenceFactor = 1
    engine.diameter = convert(1.6, "ft", "m")
    engine.length = convert(5.438, "ft", "m")
    engine.mass = PredictInstalledEngineMass(uninstalledEngineMass, numberOfEngines)
    engine.propeller = propeller
    engine.maxPower = (PW*W0) / numberOfEngines
    engine.x = convert(9.8+2.7,"ft","m")
    
    # FINISH AIRPLANE DEFINITION FOR THIS SECTION
    
    engineL = engine
    engineR = copy.deepcopy(engine)
    airplane.engines = [engineL, engineR]
    airplane.components += [engineL, engineR]
    
    ################################################################################
    # 6: LANDING GEAR DEFINITION
    ################################################################################
    
    # MAIN GEAR OBJECT
    
    mainGear = MainGear()
    
    mainGear.length = 1 # m
    mainGear.interferenceFactor = 1
    mainGear.wettedArea = convert(0, "ft^2", "m^2")
    mainGear.mass = PredictMainGearMass(airplane.initialGrossWeight, landingLoadFactor, mainGear.length)
    mainGear.x = convert(12.4,"ft","m")
    
    # FRONT GEAR OBJECT
    
    frontGear = FrontGear()
    
    frontGear.length = 1 # m
    frontGear.interferenceFactor = 1
    frontGear.wettedArea = convert(0, "ft^2", "m^2")
    frontGear.mass = PredictFrontGearMass(airplane.initialGrossWeight, landingLoadFactor, frontGear.length)
    frontGear.x = convert(4.405,"ft","m")
    
    # FINISH AIRPLANE DEFINITION FOR THIS SECTION
    
    airplane.mainGear = mainGear
    airplane.frontGear = frontGear
    airplane.components += [mainGear, frontGear]
    
    ################################################################################
    # 7: FUEL SYSTEM DEFINITION
    ################################################################################
    
    # FUEL SYSTEM OBJECT
    
    fuelSystem = FuelSystem()
    
    fuelSystem.interferenceFactor = 1
    fuelSystem.wettedArea = 0
    fuelSystem.referenceLength = 0
    fuelSystem.mass = PredictFuelSystemMass(totalFuelVolume, 0, 2, numberOfEngines)
    fuelSystem.x = convert(11.75-0.25*convert(wing.chord,"m","ft"),"ft","m")
    
    # FINISH AIRPLANE DEFINITION FOR THIS SECTION
    
    airplane.fuelSystem = fuelSystem
    airplane.components += [fuelSystem]
    
    ################################################################################
    # 8: AVIONICS DEFINITION
    ################################################################################
    
    # AVIONICS OBJECT
    
    avionics = Avionics()
    
    avionics.interferenceFactor = 1
    avionics.wettedArea = 0
    avionics.referenceLength = 0
    avionics.mass = PredictAvionicsMass(uninstalledAvionicsWeight)
    avionics.x = convert(4.85,"ft","m")
    
    # FINISH AIRPLANE DEFINITION FOR THIS SECTION
    
    airplane.avionics = avionics
    airplane.components += [avionics]
    
    ################################################################################
    # 9: MISCELLANEOUS COMPONENT DEFINITIONS
    ################################################################################
    
    # FLIGHT CONTROLS OBJECT
    
    flightControls = FlightControls()
    
    flightControls.interferenceFactor = 1
    flightControls.wettedArea = 0
    flightControls.referenceLength = 0
    flightControls.mass = PredictFlightControlsMass(fuselage.length, wing.span, sizingLoadFactor, airplane.initialGrossWeight)
    flightControls.x = convert(4.95,"ft","m")
    
    # HYDRAULICS OBJECT
    
    hydraulics = Hydraulics()
    
    hydraulics.interferenceFactor = 1
    hydraulics.wettedArea = 0
    hydraulics.referenceLength = 0
    hydraulics.mass = PredictHydraulicsMass(airplane.initialGrossWeight)
    hydraulics.x = convert(12.4,"ft","m")
    
    # ELECTRONICS OBJECT
    
    electronics = Electronics()
    
    electronics.interferenceFactor = 1
    electronics.wettedArea = 0
    electronics.referenceLength = 0
    electronics.mass = PredictElectronicsMass(fuelSystem.mass, avionics.mass)
    electronics.x = convert(4.7,"ft","m")
    
    # AIRCONICE OBJECT
    
    airConIce = AirConIce()
    
    airConIce.interferenceFactor = 1
    airConIce.wettedArea = 0
    airConIce.referenceLength = 0
    airConIce.mass = PredictAirConIceMass(airplane.initialGrossWeight, airplane.pilots + airplane.passengers, avionics.mass, cruiseMachNumber)
    airConIce.x = convert(3*convert(wing.chord,"m","ft")/4,"ft","m") + wing.x
    
    # FURNISHINGS OBJECT
    
    furnishings = Furnishings()
    
    furnishings.interferenceFactor = 1
    furnishings.wettedArea = 0
    furnishings.referenceLength = 0
    furnishings.mass = PredictFurnishingsMass(airplane.initialGrossWeight)
    furnishings.x = convert(10.24,"ft","m")
    
    # FINISH AIRPLANE DEFINITION FOR THIS SECTION

    airplane.components += [flightControls, hydraulics, electronics, airConIce, furnishings]

    # DEFINE PAYLOAD INFORMATION
    passengerPayload = Passengers()
    passengerPayload.x = convert((1*7.143+2*10.238+2*13.095)/5,"ft","m")
    passengerPayload.mass = CalculatePassengerPayloadMass(airplane.passengers)

    baggagePayload = Baggage()
    baggagePayload.x = convert(14,"ft","m")
    baggagePayload.mass = CalculateBaggageMass(airplane.passengers)

    pilotPayload = Pilot()
    pilotPayload.x = convert(7.143,"ft","m")
    pilotPayload.mass = CalculatePilotPayloadMass(airplane.pilots)

    airplane.payloads = [passengerPayload, baggagePayload, pilotPayload]
    ################################################################################
    # FINISH DEFINING AIRPLANE
    ################################################################################

    airplane.emptyMass = sum([component.mass for component in airplane.components])

    ################################################################################

    return airplane
