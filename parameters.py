from utilities import *
from convert import convert
from scipy import *

################################################################################

class Mission:
    segments = None
    
    def simulate(Airplane): # TODO: is this the best place to define this?
        pass

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
    
    def __init__(self, name):
        self.name = name
    
    def initialize(Airplane, t, t0): # reset the airplane parameters to simulate going forward, t is total mission time elapsed, t0 is the beginning time of the mission segment
        pass
    
    def checkComplete(Airplane, t, t0): # returns true when mission segment has been completed, t is total mission time elapsed, t0 is the beginning time of the mission segment
        pass
        
    def update(Airplane, t, tstep): # TODO: write comment
        pass

class Airplane:
    altitude = None # number [m] : (0 <= x)
    position = None # number [m] : (0 <= x) # how far the airplane has gone so far
    speed = None # number [m/s]
    throttle = None # number : (0 <= x <= 1)
    pilots = None # number : (0 < x)
    passengers = None # number : (0 <= x)
    flightPathAngle = None # < 5 degrees
    wing = None # wing component object
    engines = [] # [engine object] # list of engines on airplane
    components = [] # [component objects] # list of components making up airplane (including wing)
    oswaldEfficiencyFactor = None # number : (0.7 < x < 0.85) # fix later maybe
    compressibilityDrag = 0 # number : (0 = x) # we fly too slow
    miscellaneousParasiteDragFactor = None # number : (0 <= x)

################################################################################
# COMPONENTS
################################################################################

class Propeller:
    diameter = None # number [m] : (0 <= x)
    angularVelocity = None # number [rad/s] : (0 <= x) # 0<=x assumes no fanning of engine to regain energy
    efficiency = None

class Engine: # the engines or motors that drive the propeller
    maxPower = None # number [W] : (0 <= x)

class Powerplant: # the powerplant system configuration
    gas = None # fuel object
    battery = None # fuel object
    generator = None # generator object
    percentElectric = None # number : (0 <= x <= 1) # how much of the output energy comes from electricity
    generatorOn = None # bool # is the generator on, giving energy to the battery?

class Fuel:
    mass = None # number [kg] : (0 <= x)
    energyDensity = None # number [J/kg] : (0 <= x)

class Generator:
    pass

class Component:
    formFactor = None # number : (?)
    interferenceFactor = None # number : (?)
    wettedArea = None # number [m^2] : (0 <= x)
    referenceLength = None # number [m] : (0 <= x)

class Fuselage(Component):
    diameter = None # number [m] : (0 <= x)
    length = None # number [m]
    
    def __init__(self, interferenceFactor, diameter, length):
        self.interferenceFactor = interferenceFactor
        self.referenceLength = diameter
        self.diameter = diameter
        self.length = length
    
    @property
    def finenessRatio(self):
        return self.length / self.diameter
    
    @property
    def formFactor(self):
        return 1 + 60 / self.finenessRatio**3 + self.finenessRatio / 400
        
    @property
    def wettedArea(self):
        # ASSUMPTION: modeling as "hotdog"
        return pi * self.diameter * self.length * (1 - 2/self.finenessRatio)**(2/3) * (1 + 1/self.finenessRatio**2)

class Nacelle(Component):
    diameter = None
    length = None
    
    def __init__(self, interferenceFactor, diameter, length):
        self.interferenceFactor = interferenceFactor
        self.referenceLength = diameter
        self.diameter = diameter
        self.length = length
    
    @property
    def finenessRatio(self):
        return self.length / self.diameter
    
    @property
    def formFactor(self):
        return 1 + 0.35 / self.finenessRatio
    
    @property
    def wettedArea(self):
        # ASSUMPTION: modeling as a cylinder
        return pi * self.diameter * self.length

class Surface(Component):
    planformArea = None
    thicknessToChord = None
    
    def __init__(self, interferenceFactor, planformArea, thicknessToChord, span):
        self.interferenceFactor = interferenceFactor
        self.referenceLength = span
        self.thicknessToChord = thicknessToChord
        self.planformArea = planformArea
    
    @property
    def formFactor(self):
        Zfactor = 2 # FIXME: PLEASE: the Z factor depends on the Mach at which you are flying, for us its between 0 and 0.3, 1.7<Z<2
        return 1 + Zfactor * self.thicknessToChord + 100 * self.thicknessToChord**4
    
    @property
    def wettedArea(self):
        # ASSUMPTION: modeling as a cylinder
        return self.planformArea * 2 * 1.02

class Wing(Surface):
    span = None # number [m] : (0 <= x)
    aspectRatio = None # number : (0 <= x)
    chord = None # number [m] : (0 <= x)