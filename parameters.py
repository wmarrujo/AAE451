# LOCAL DEPENDENCIES        print(airplane.passengers)

from utilities import *
from constants import *

# EXTERNAL DEPENDENCIES

from scipy import *
import sys

################################################################################

class Mission:
    segments = None
    cruiseRange = None

    def simulate(self, tstep, airplane, recordingFunction=(lambda t, s, a: None), silent=False):
        """
        takes a time step, an airplane definition, and an optional recording function to run each iteration
        returns the success of the simulation. If it was able to complete it, it returns True, if it encountered something that broke the verification, it returns False

        the recording function takes the simulation time, the segment name, and the airplane in its current state

        """
        tstepBase = tstep
        airplane.passengers = ceil(self.passengerFactor*airplane.maxPassengers)
        t = 0 # s
        iteration = 0
        verified = verifySimulation(iteration, t, "Start", airplane)
        self.segments[0].initialize(airplane, t, t) # make airplane valid before the recording function
        recordingFunction(t, "start", airplane)
        printSimulationProgressBar(iteration) if not silent else None

        for segment in self.segments:
            t0 = t
            segment.initialize(airplane, t, t0)
            tstep = tstepBase * segment.stepSizeFraction

            while verified and not segment.completed(airplane, t, t0):
                try:
                    segment.update(airplane, t, tstep)

                    # hard bounds so it doesn't crash
                    if airplane.altitude < 0:
                        airplane.altitude = 0

                    verified = verifySimulation(iteration, t, segment.name, airplane) # here to make sure the simulation doesn't run forever
                except (KeyboardInterrupt, SystemExit): # if you quit it, actually quit
                    raise
                except Exception as e: # otherwise, keep going
                    exception_type, exception_value, exception_traceback = sys.exc_info()
                    print("The Simulation Encountered an Error: ", exception_value)
                    verified = False
                recordingFunction(t, segment.name, airplane)
                printSimulationProgressBar(iteration, message=segment.name) if not silent else None

                t = t + tstep
                iteration += 1
            if not verified:
                break # get out of the for loop too

        printSimulationProgressBar(iteration, ended=True, message="succeeded" if verified else "failed") if not silent else None
        if verified:
            return airplane
        else:
            return None

def verifySimulation(iteration, t, segmentName, airplane):
    if iterationCap <= iteration:
        print("WARNING: simulation iteration cap reached")
        return False
    if timeCap <= t:
        print("WARNING: simulation time cap reached")
        return False
    return True

def printSimulationProgressBar(iteration, ended=False, message=""):
    barLength = int(ceil(iteration / 400))
    bar = "╶"*(barLength-8) + "────━━ ✈︎"[-barLength-2:]
    if not ended:
        print("\rSimulating ({:6d}): {} {}              ".format(iteration, bar, message), end="", flush=True)
    else: # ended
        print("\rSimulating ({:6d}): {} ".format(iteration, bar), end="", flush=True)
        print("║ DONE! {}".format(message))

class Segments:
    segments = None

    def __init__(self, segments):
        self.segments = segments

    def __getitem__(self, key):
        if type(key) is int:
            return self.segments[key]
        elif type(key) is str:
            return first(self.segments, lambda x: x.name == key)

class Segment:
    name = None
    stepSizeFraction = 1

    def __init__(self, name):
        self.name = name

    def initialize(Airplane, t, t0): # reset the airplane parameters to simulate going forward, t is total mission time elapsed, t0 is the beginning time of the mission segment
        pass

    def checkComplete(Airplane, t, t0): # returns true when mission segment has been completed, t is total mission time elapsed, t0 is the beginning time of the mission segment
        pass

    def update(Airplane, t, tstep): # TODO: write comment
        pass

class Airplane:
    name = None # string : name of the airplane (mostly so that we can name simulation files uniquely)
    altitude = None # number [m] : (0 <= x)
    position = None # number [m] : (0 <= x) # how far the airplane has gone so far
    speed = None # number [m/s]
    throttle = None # number : (0 <= x <= 1)
    pilots = None # number : (0 < x)
    passengers = None # number : (0 <= x)
    pitch = None # number [rad]
    flightPathAngle = None # number [rad]
    wing = None # wing component object
    engines = [] # [engine object] # list of engines on airplane
    powerplant = None # powerplant object
    components = [] # [component objects] # list of components making up airplane (including wing)
    payloads = [] # [payload objects] # list of payloads making up airplane
    oswaldEfficiencyFactor = None # number : (0.7 < x < 0.85) # TODO: get better estimate
    compressibilityDrag = 0 # number : (0 = x) # we fly too slow
    miscellaneousParasiteDragFactor = None # number : (0 <= x)
    initialGrossWeight = None # number : initial guess for gross weight, changes with iteration
    horizontalStabilizer = None # HorizontalStabilizer object
    verticalStabilizer = None # VerticalStabilizer object
    fuelSystem = None # FuelSystem object
    avionics = None # Avionics object
    emptyMass = None # number [kg] : (0 <= x) # set once at the beginning (for algorithm optimization)

    @property
    def angleOfAttack(self):
        p = self.pitch
        fpA = self.flightPathAngle

        return p - fpA
    @angleOfAttack.setter
    def angleOfAttack(self, a):
        self.pitch = a + self.flightPathAngle # add the angle of attack to the flight path angle

################################################################################
# COMPONENTS
################################################################################

class Propeller:
    diameter = None # number [m] : (0 <= x)
    efficiency = None

class Powerplant: # the powerplant system configuration
    gas = None # gas object
    battery = None # battery object
    generator = None # generator object
    percentElectric = None # number : (0 <= x <= 1) # how much of the output energy comes from electricity
    generatorOn = None # bool # is the generator on, giving energy to the battery?
    SFC = None # engine SFC

    @property
    def fuelMass(self):
        mg = self.gas.mass if self.gas is not None else 0
        mb = self.battery.mass if self.battery is not None else 0

        return mg + mb

    @fuelMass.setter
    def fuelMass(self, m):
        edg = self.gas.energyDensity if self.gas else 0
        edb = self.battery.energyDensity if self.battery else 0
        p = self.percentElectric

        if 0 < p and p < 1: # hybrid
            self.gas.mass = m*edb*(1-p) / (edg*p + edb*(1-p))
            self.battery.mass = m*edg*p / (edb*(1-p) + edg*p)
            self.battery.capacity = self.battery.mass / edb
        if p == 0: # fully gas
            self.gas.mass = m
        if p == 1: # fully battery
            self.battery.mass = m
            self.battery.capacity = self.battery.mass / edbn # Sarah

    @property
    def emptyFuelMass(self):
        mb = self.battery.mass if self.battery is not None else 0 # TODO: approximation that battery mass is constant with charge & stuff

        return mb

class Gas:
    mass = None # number [kg] : (0 <= x)
    energyDensity = None # number [J/kg] : (0 <= x)
    density = None # number [kg/m^3] : (0 <= x)
    x = None # number [m]

class Battery:
    mass = None # number [kg] : (0 <= x)
    energyDensity = None # number [W*h/kg] : (0 <= x)
    capacity = None # number [J] : (0 <= x)
    charge = None # number : (0 <= x <= 1)
    x = None # number [m]

    @property
    def energy(self):
        E = self.capacity
        C = self.charge

        return E*C

    @energy.setter
    def energy(self, E):
        self.charge = E / self.capacity

class Generator:
    efficiency = None # number : (0 <= x <= 1)
    power = None # number : (0 <= x) # most efficient power setting, the only one we'll run it at

class Component:
    mass = None # number : (0 <= x)
    interferenceFactor = None # number : (1 <= x)
    wettedArea = None # number [m^2] : (0 <= x)
    referenceLength = None # number [m] : (0 <= x)
    x = None # number [m] : -- location from reference datum for CG calcs

    def formFactor(self, airplane):
        return 0 # default, to be overwritten if defined # TODO: put this independently in each component class definition, not a default value

class Payload:
    mass = None
    x = None

class Engine(Component): # the engines/motors that drive the propeller
    maxPower = None # number [W] : (0 <= x)
    propeller = None # propeller object
    length = None # number [m] : (0 <= x)

    @property
    def diameter(self):
        return self.referenceLength
    @diameter.setter
    def diameter(self, d):
        self.referenceLength = d

    @property
    def finenessRatio(self):
        l = self.length
        D = self.diameter

        return l / D

    def formFactor(self, airplane):
        fr = self.finenessRatio

        return 1 + 0.35 / fr

    @property
    def wettedArea(self):
        d = self.diameter
        l = self.length

        return pi * d * l # ASSUMPTION: modeling as a cylinder

class Fuselage(Component):
    length = None # number [m]

    @property
    def diameter(self):
        return self.referenceLength
    @diameter.setter
    def diameter(self, d):
        self.referenceLength = d

    @property
    def finenessRatio(self):
        l = self.length
        D = self.diameter

        return l / D

    def formFactor(self, airplane):
        fr = self.finenessRatio

        return 1 + 60 / fr**3 + fr / 400

    @property
    def wettedArea(self):
        D = self.diameter
        l = self.length
        fr = self.finenessRatio

        return pi * D * l * (1 - 2/fr)**(2/3) * (1 + 1/fr**2) # ASSUMPTION: modeling as "hotdog"

class Surface(Component):
    planformArea = None # number [m^2] : (0 <= x)
    thicknessToChord = None # number : (0 <= x)
    airfoil = None # airfoil object
    sweep = None # IN RADIANS
    taperRatio = None # taper ratio

    def setPlanformAreaHoldingAspectRatio(self, S):
        AR = self.aspectRatio
        self.planformArea = S
        self.span = sqrt(AR * S) # set the span

    def setAspectRatioHoldingSpan(self, AR):
        b = self.span
        self.planformArea = b**2/AR

    def setAspectRatioHoldingPlanformArea(self, AR):
        S = self.planformArea
        self.span = sqrt(AR*S)

    def formFactor(self, airplane):
        #Zfactor = 2 # FIXME: PLEASE: the Z factor depends on the Mach at which you are flying, for us its between 0 and 0.3, 1.7<Z<2
        V = Airplane.speed
        if V is None:
            V = 0
        a = machAtAltitude(0)
        M = V / a
        Zfactor = (2-M**2)/(sqrt(1-M**2))
        tc = self.thicknessToChord

        return 1 + Zfactor * tc + 100 * tc**4

    @property
    def wettedArea(self):
        S = self.planformArea
        tc = self.thicknessToChord

        return S * 2 * (1+tc) # ASSUMPTION: modeling as a cylinder

    @property
    def aspectRatio(self):
        S = self.planformArea
        b = self.span

        return b**2/S

    @property
    def span(self):
        return self.referenceLength
    @span.setter
    def span(self, b):
        self.referenceLength = b

    @property
    def chord(self):
        b = self.referenceLength
        AR = self.aspectRatio

        return b/AR

class Wing(Surface):
    @property
    def maximumLiftCoefficient(self):
        maxCL = self.airfoil.maximumLiftCoefficient

        return maxCL

class HorizontalStabilizer(Surface):
    pass

class VerticalStabilizer(Surface):
    pass

class MainGear(Component):

    @property
    def length(self):
        return self.referenceLength
    @length.setter
    def length(self, l):
        self.referenceLength = l

class FrontGear(Component):

    @property
    def length(self):
        return self.referenceLength
    @length.setter
    def length(self, l):
        self.referenceLength = l

class FuelSystem(Component):
    pass

class FlightControls(Component):
    pass

class Hydraulics(Component):
    pass

class Avionics(Component):
    pass

class Electronics(Component):
    pass

class AirConIce(Component):
    pass

class Furnishings(Component):
    pass

class Passengers(Payload):
    pass

class Baggage(Payload):
    pass

class Pilot(Payload):
    pass

class Airfoil:
    data = None # the dictionary containing aerodynamic information

    def __init__(self, filepath):
        self.data = CSVToDict(filepath)

    def liftCoefficientAtAngleOfAttack(self, angleOfAttack):
        a = convert(angleOfAttack, "rad", "deg") # gets angleOfAttack in radians, csv in degrees
        f = functionFromPairs(pairsFromColumns(self.data, "alpha", "CL"))

        return f(a)

    def dragCoefficientAtAngleOfAttack(self, angleOfAttack):
        a = convert(angleOfAttack, "rad", "deg") # gets angleOfAttack in radians, csv in degrees
        f = functionFromPairs(pairsFromColumns(self.data, "alpha", "CD"))

        return f(a)

    @property
    def minimumDefinedAngleOfAttack(self):
        return convert(float(self.data["alpha"][0]), "deg", "rad")

    @property
    def maximumDefinedAngleOfAttack(self):
        return convert(float(self.data["alpha"][-1]), "deg", "rad")

    @property
    def maximumLiftCoefficient(self):
        CLs = [float(cl) for cl in self.data["CL"]]

        return max(CLs)
