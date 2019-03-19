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
        
    def update(Airplane, t, tstep): # TODO: write comment
        pass

class Airplane:
    altitiude = None # number [m] : (0 <= x)
    position = None # number [m] : (0 <= x) # how far the airplane has gone so far
    speed = None # number [m/s]
    throttle = None # number : (0 <= x <= 1)
    mass = None # number : (0 <= x)
    wing = None # wing component object
    engines = [] # [engine object] # list of engines on airplane
    
    propeller = None # propeller object
    powerplant = None # powerplant object
    extraComponents = [] # all other components not mentioned in rest of definition
    miscellaneousParasiteDragFactor = None

################################################################################
# COMPONENTS
################################################################################

class Propeller:
    diameter = None # number [m] : (0 <= x)
    thrust = None # number [N] : (0 <= x)
    angularVelocity = None # number [rad/s] : (0 <= x) # 0<=x assumes no fanning of engine to regain energy

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

class Wing:
    span = None # number [m] : (0 <= x)