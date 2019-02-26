from convert import convert
from scipy import *

################################################################################

class Mission:
    passengers = None
    pilots = None
    segment = {
        "startup": {},
        "takeoff": {},
        "climb": {},
        "cruise": {},
        "descent": {},
        "abortClimb": {},
        "loiter": {},
        "abortDescent": {},
        "landing": {},
        "shutdown": {}
        }
    segments = ["takeoff", "climb", "cruise", "descent", "abortClimb", "loiter", "abortDescent", "landing", "shutdown"]


class Airplane:
    etap = None
    thrust = None
    power = None
    velocity = None
    Cbhp = None
    propellerRotationSpeed = None
    propellerDiameter = None
    takeoffWeight = None
    #chord = None
    #span = None
    #aspectRatio = None
    #tryhicktoChord = None
    #taperRatio = None
    #wingTwist = None
    #fuselageFineness = None
    #LDcruise = None
    maxPowerToWeight = None
    wingLoading = None
    powerplant = None
    components = []
    miscellaneousParasiteDragFactor = None

################################################################################
# COMPONENTS
################################################################################

class Powerplant:
    percentEnergyFromBattery = None

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

# nacelles
# wings
# struts
# pylons
# fuselage
# landing gear
# tail
