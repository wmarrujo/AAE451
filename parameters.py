from utilities import *
from csvTools import *
from convert import convert
from scipy import *

################################################################################

class Mission:
    segments = None
    
    def simulate(self, tstep, Airplane, recordingFunction):
        t0 = 0 # s
        t = t0
        iteration = 0
        recordingFunction(t, "Start", Airplane)
        
        for segment in self.segments:
            segment.initialize(Airplane, t, t0)
            
            while not segment.completed(Airplane, t, t0):
                segment.update(Airplane, t, tstep)
                recordingFunction(t, segment.name, Airplane)
                
                t = t + tstep
                iteration += 1

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
    powerplant = None # powerplant object
    components = [] # [component objects] # list of components making up airplane (including wing)
    oswaldEfficiencyFactor = None # number : (0.7 < x < 0.85) # TODO: get better estimate
    compressibilityDrag = 0 # number : (0 = x) # we fly too slow
    miscellaneousParasiteDragFactor = None # number : (0 <= x)
    emptyWeight = None # number [N] : (0 <= x) # TODO: replace with component weight, will delete this parameter later
    angleOfAttack = None # number [rad]

################################################################################
# COMPONENTS
################################################################################

class Propeller:
    diameter = None # number [m] : (0 <= x)
    angularVelocity = None # number [rad/s] : (0 <= x) # 0<=x assumes no fanning of engine to regain energy
    efficiency = None

class Engine: # the engines/motors that drive the propeller
    maxPower = None # number [W] : (0 <= x)
    propeller = None # propeller object

class Powerplant: # the powerplant system configuration
    gas = None # gas object
    battery = None # battery object
    generator = None # generator object
    percentElectric = None # number : (0 <= x <= 1) # how much of the output energy comes from electricity
    generatorOn = None # bool # is the generator on, giving energy to the battery?
    
    
    @property
    def fuelMass(self):
        mg = self.gas.mass if self.gas is not None else 0
        mb = self.battery.mass if self.battery is not None else 0
        
        return mg + mb

class Gas:
    mass = None # number [kg] : (0 <= x)
    energyDensity = None # number [J/kg] : (0 <= x)

class Battery:
    mass = None # number [kg] : (0 <= x)
    energyDensity = None # number [W*h/kg] : (0 <= x)
    energy = None # number [J] : (0 <= x)
    
class Generator:
    efficiency = None # number : (0 <= x <= 1)
    power = None # number : (0 <= x) # most efficient power setting, the only one we'll run it at

class Component:
    mass = None # number : (0 <= x)
    formFactor = None # number : (1 <= x)
    interferenceFactor = None # number : (1 <= x)
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
        l = self.length
        D = self.diameter
        
        return l / D
    
    @property
    def formFactor(self):
        fr = self.finenessRatio
        
        return 1 + 60 / fr**3 + fr / 400
        
    @property
    def wettedArea(self):
        D = self.diameter
        l = self.length
        fr = self.finenessRatio
        
        return pi * D * l * (1 - 2/fr)**(2/3) * (1 + 1/fr**2) # ASSUMPTION: modeling as "hotdog"

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
        l = self.length
        D = self.diameter
        
        return l / D
    
    @property
    def formFactor(self):
        fr = self.finenessRatio
        
        return 1 + 0.35 / fr
    
    @property
    def wettedArea(self):
        d = self.diameter
        l = self.length
        
        return pi * d * l # ASSUMPTION: modeling as a cylinder

class Surface(Component):
    planformArea = None # number [m^2] : (0 <= x)
    thicknessToChord = None # number : (0 <= x)
    airfoil = None # airfoil object
    
    def __init__(self, interferenceFactor, planformArea, thicknessToChord, span):
        self.interferenceFactor = interferenceFactor
        self.referenceLength = span
        self.thicknessToChord = thicknessToChord
        self.planformArea = planformArea
    
    @property
    def formFactor(self):
        Zfactor = 2 # FIXME: PLEASE: the Z factor depends on the Mach at which you are flying, for us its between 0 and 0.3, 1.7<Z<2
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
        
        return S/b
    
    @property
    def span(self):
        return self.referenceLength
    
    @property
    def chord(self):
        b = self.span
        AR = self.aspectRatio
        
        return AR/b

class Wing(Surface):
    maximumLiftCoefficient = None # number

class Airfoil:
    data = None # the dictionary containing aerodynamic information
    
    def __init__(self, filepath):
        self.data = CSVToDict(filepath)
    
    def liftCoefficientAtAngleOfAttack(self, angleOfAttack):
        a = angleOfAttack*180/pi # gets angleOfAttack in radians, csv in degrees
        f = functionFromPairs(pairsFromColumns(self.data, "alpha", "CL"))
        
        return f(a)
    
    @property
    def maximumLiftCoefficient(self):
        CLs = self.data["CL"]
        
        return max(CLs)