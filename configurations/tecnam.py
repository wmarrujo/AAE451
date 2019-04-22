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
    sizingLoadFactor = 3.8
    landingLoadFactor = 2.67 * 1.5
    horizontalTailVolumeCoefficient = 0.80
    verticalTailVolumeCoefficient = 0.07
    numberOfEngines = 2
    uninstalledEngineMass = 65.7 # kg
    totalFuelVolume = convert(50, "gal", "m^3")
    uninstalledAvionicsWeight = 15*9.8 # N # FIXME: you sure?
    cruiseMachNumber = convert(180, "kts", "m/s") / machAtAltitude(cruiseAltitude)
    #Composite pieces (1 = comp, 0 = alloy)
    compositeWing = 0
    compositeFuselage = 0
    compositeHorizontalStabilizer = 0
    compositeVerticalStabilizer = 0


    ################################################################################
    # 0: AIRPLANE OBJECT INITIALIZATION
    ################################################################################

    airplane = Airplane()

    airplane.initialGrossWeight = W0
    airplane.pilots = 1
    airplane.passengers = 0
    airplane.maxPassengers = 3
    airplane.oswaldEfficiencyFactor = 0.8
    airplane.compressibilityDragCoefficient = 0
    airplane.miscellaneousParasiteDragFactor = 0.004 # FIXME: what should this be?
    airplane.compositeFraction = 0 # Percent of airframe that is composite materials
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

    # FINISH AIRPLANE DEFINITION FOR THIS SECTION

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
    wing.setAspectRatioHoldingPlanformArea(7)
    wing.thicknessToChord = 0.02
    wing.sweep = 0
    wing.taperRatio = 1
    wing.mass = PredictWingMass(wing.span, wing.aspectRatio, wing.chord, sizingLoadFactor, wing.sweep, wing.taperRatio, wing.planformArea, airplane.initialGrossWeight, powerplant.fuelMass*g, cruiseDynamicPressure, wing.thicknessToChord, compositeWing)
    wing.x = 4 # [m]

    # FINISH AIRPLANE DEFINITION FOR THIS SECTION

    airplane.wing = wing
    airplane.components += [wing]

    ################################################################################
    # 3: FUSELAGE DEFINITION
    ################################################################################

    # FUSELAGE OBJECT

    fuselage = Fuselage()

    fuselage.interferenceFactor = 1
    fuselage.diameter = 1.4 # m
    fuselage.length = 8.7 # m
    fuselage.mass = PredictFuselageMass(fuselage.wettedArea, airplane.initialGrossWeight, fuselage.length, fuselage.diameter, cruiseDynamicPressure, 0, sizingLoadFactor, compositeFuselage)
    fuselage.x = fuselage.length / 2 # [m]

    # FINISH AIRPLANE DEFINITION FOR THIS SECTION

    airplane.fuselage = fuselage
    airplane.components += [fuselage]

    ################################################################################
    # 4: TAIL DEFINITION
    ################################################################################

    # HORIZONTAL STABILIZER OBJECT

    horizontalStabilizer = HorizontalStabilizer()

    horizontalStabilizer.interferenceFactor = 1.2
    horizontalStabilizer.planformArea = 2.64 # m^2
    horizontalStabilizer.thicknessToChord = 0.12
    horizontalStabilizer.sweep = 0
    horizontalStabilizer.taperRatio = 1
    horizontalStabilizer.mass = PredictHorizontalStabilizerMass(airplane.initialGrossWeight, sizingLoadFactor, horizontalStabilizer.taperRatio, horizontalStabilizer.sweep, wing.taperRatio, horizontalTailVolumeCoefficient, wing.span, wing.chord, 0.5 * fuselage.length, cruiseDynamicPressure, wing.thicknessToChord, compositeHorizontalStabilizer)
    horizontalStabilizer.x = 8.6 # [m]

    # VERTICAL STABILIZER OBJECT

    verticalStabilizer = VerticalStabilizer()

    verticalStabilizer.interferenceFactor = 1.1
    verticalStabilizer.planformArea = 2.86 # m^2
    verticalStabilizer.thicknessToChord = 0.12
    verticalStabilizer.span = convert(6, "ft", "m")
    verticalStabilizer.sweep = convert(20, "deg", "rad")
    verticalStabilizer.taperRatio = 1
    verticalStabilizer.mass = PredictVerticalStabilizerMass(verticalStabilizer.taperRatio, verticalStabilizer.sweep, sizingLoadFactor, 0, airplane.initialGrossWeight, cruiseDynamicPressure, verticalTailVolumeCoefficient, 0.6 * fuselage.length, wing.span, wing.chord, wing.planformArea, wing.thicknessToChord, compositeVerticalStabilizer)
    verticalStabilizer.x = 8.65 # [m]

    # FINISH AIRPLANE DEFINITION FOR THIS SECTION

    airplane.horizontalStabilizer = horizontalStabilizer
    airplane.verticalStabilizer = verticalStabilizer

    airplane.components += [horizontalStabilizer, verticalStabilizer]

    ################################################################################
    # 5: ENGINE DEFINITION
    ################################################################################

    # PROPELLER OBJECT

    propeller = Propeller()

    propeller.diameter = 1.65 # m
    propeller.efficiency = 0.9

    # ENGINE OBJECT

    engine = Engine()

    engine.interferenceFactor = 1
    engine.diameter = 0.65 # m
    engine.length = 1.8 # m
    engine.mass = PredictInstalledEngineMass(uninstalledEngineMass, numberOfEngines) / numberOfEngines
    engine.propeller = propeller
    engine.maxPower = (PW*W0) / numberOfEngines
    engine.x = wing.x - wing.chord/2 # [m]

    # engine.maxPower = convert(98.6, "hp", "W")

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

    mainGear.length = 0.4 # m
    mainGear.interferenceFactor = 1
    mainGear.wettedArea = 0
    mainGear.mass = PredictMainGearMass(airplane.initialGrossWeight, airplane.powerplant.gas.mass, landingLoadFactor, mainGear.length)
    mainGear.x = 5.5 # [m]
    mainGear.retractable = True #Is landing Gear retractable?

    # FRONT GEAR OBJECT

    frontGear = FrontGear()

    frontGear.length = 0.5 # m
    frontGear.interferenceFactor = 1
    frontGear.wettedArea = 0
    frontGear.mass = PredictFrontGearMass(airplane.initialGrossWeight, landingLoadFactor, frontGear.length)
    frontGear.x = 2 # [m]

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
    fuelSystem.x = wing.x - wing.chord / 4 # [m]

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
    avionics.x = 1.5 # [m]

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
    flightControls.x = avionics.x + .1 # [m]

    # HYDRAULICS OBJECT

    hydraulics = Hydraulics()

    hydraulics.interferenceFactor = 1
    hydraulics.wettedArea = 0
    hydraulics.referenceLength = 0
    hydraulics.mass = PredictHydraulicsMass(airplane.initialGrossWeight)
    hydraulics.x = (mainGear.x + frontGear.x) / 2 # [m] -- assume the bulk of the hydraulics mass is between the front and main gear

    # ELECTRONICS OBJECT

    electronics = Electronics()

    electronics.interferenceFactor = 1
    electronics.wettedArea = 0
    electronics.referenceLength = 0
    electronics.mass = PredictElectronicsMass(fuelSystem.mass, avionics.mass)
    electronics.x = avionics.x - .1 # [m] -- Assume most of the electronics mass (likely the battery for )

    # AIRCONICE OBJECT

    airConIce = AirConIce()

    airConIce.interferenceFactor = 1
    airConIce.wettedArea = 0
    airConIce.referenceLength = 0
    airConIce.mass = PredictAirConIceMass(airplane.initialGrossWeight, airplane.pilots + airplane.maxPassengers, avionics.mass, cruiseMachNumber)
    airConIce.x = 3.5 # [m] #GUESS

    # FURNISHINGS OBJECT

    furnishings = Furnishings()

    furnishings.interferenceFactor = 1
    furnishings.wettedArea = 0
    furnishings.referenceLength = 0
    furnishings.mass = PredictFurnishingsMass(airplane.initialGrossWeight)
    furnishings.x = 2.3 # [m] (SPLIT INTO SEATS??)

    # DEFINE PAYLOAD

    passengerPayload = Passengers()
    passengerPayload.x = 2.5
    passengerPayload.mass = CalculatePassengerPayloadMass(airplane.maxPassengers)

    baggagePayload = Baggage()
    baggagePayload.x = 3
    baggagePayload.mass = CalculateBaggageMass(airplane.maxPassengers)

    pilotPayload = Pilot()
    pilotPayload.x = 2
    pilotPayload.mass = CalculatePilotPayloadMass(airplane.pilots)

    airplane.payloads = [passengerPayload, baggagePayload, pilotPayload]


    # FINISH AIRPLANE DEFINITION FOR THIS SECTION

    airplane.components += [flightControls, hydraulics, electronics, airConIce, furnishings]

    ################################################################################
    # FINISH DEFINING AIRPLANE
    ################################################################################

    airplane.emptyMass = sum([component.mass for component in airplane.components])

    ################################################################################

    return airplane
