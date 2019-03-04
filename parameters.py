from utilities import *
from convert import convert
from scipy import *

################################################################################

class Mission:
    passengers = None
    pilots = None
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

class Airplane:
    altitiude = None # number : (0 <= altitude)
    position = None # number : (0 <= range) # how far the airplane has gone so far
    speed = None # number
    throttle = None # number : (0 <= throttle <= 1)
    emptyMass = None # number : (0 <= emptyMass)
    installedPower = None # number : (0 <= installedPower)
    wing = None # wing component object
    powerplant = None # powerplant object
    extraComponents = [] # all other components not mentioned in rest of definition
    miscellaneousParasiteDragFactor = None

################################################################################
# COMPONENTS
################################################################################

class Powerplant:
    percentEnergyFromBattery = None
    fuelMass = None # number : (0 <= fuelMass)
    def useEnergy():
        pass

class Component:
    formFactor = None
    interferenceFactor = None
    wettedArea = None
    referenceLength = None
    
    def reynoldsNumber(self, density, velocity, dynamicViscosity):
        return density * velocity * self.referenceLength / dynamicViscosity
    
    def skinFrictionCoefficient(self, density, velocity, dynamicViscosity):
        return 0.455 / (log10(self.reynoldsNumber(density, velocity, dynamicViscosity))**2.58)

class Fuselage(Component):
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
    pass

# nacelles
# wings
# struts
# pylons
# fuselage
# landing gear
# tail
