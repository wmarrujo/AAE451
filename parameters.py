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
    compressibilityDragCoefficient = 0 # number : (0 = x) # we fly too slow
    miscellaneousParasiteDragFactor = None # number : (0 <= x)
    InitialGrossWeight = None # number : initial guess for gross weight, changes with iterations
    emptyWeight = None # number [N] : (0 <= x) # TODO: replace with component weight, will delete this parameter later
    angleOfAttack = None # number [rad]
    # takeoffLiftCoefficient = 1.5  # number : (0 <= x) # based on Anderson table 5.3 for plain flap # FIXME: figure out this takeoff/landing thing
    # landingLiftCoefficient = 1.85  # number : (0 <= x) # based on Anderson table 5.3 for plain flap
    productionQuantityNeeded = None  # number [planes] : (0 <= x)
    numberFlightTestAircraft = None  # number [planes] : (2 <= x <= 6)  # Raymer v6 18.4.2
    avionicsCost = None  # number [USD] : (0 <= x)
    tail = None # tail object
    
    @property
    def angleOfAttack(self):
        p = self.pitch
        fpA = self.flightPathAngle
        
        return p - fpA

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
    cost = None # number [USD] : (0 <= x)
    nacelle = None # nacelle object

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
    # DEBUG: Nz = None #FIXME do we use a different load factor? 3 or something?
    
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
    
    @property
    def weight(self):
        Sf = self.wettedArea
        # Wdg = airplane.InitialGrossWeight #FIXME where do we pull the guess W0 from?
        # Lt = 0.45*length #Based roughly on Tecnam Lt to L ratio
        # LD = length / diameter #CHANGE FOR ELIPTICAL (or other) FUSELAGE
        # q = .5 * densityAtAltitude(cruiseAltitude) * convert(180, "knots", "m/s") ** 2 #Dynamic prressure at cruise
        # Wpress = 0 #no pressurization weight penalty for our a/class
        # WfImperial = 0.052 * convert(Sf, "m^2", "ft^2")**1.086 * (Nz*convert(Wdg, "N", "lb")**0.177 * convert(Lt, "m^2", "ft^2")**-0.051 * LD**-0.072 * convert(q, "N/m^2","lb/ft^2")**0.241 + Wpress #RAYMER eqn 15.48
        # Nz = 1 # FIXME: do we use a different load factor? 3 or something?
        # Wdg = 1 # FIXME: where do we pull the guess W0 from?
        # Lt = 0.45*length # Based roughly on Tecnam Lt to L ratio # FIXME: don't hardcode, pass in based on airplane configuration
        # LD = length / diameter # CHANGE FOR ELIPTICAL (or other) FUSELAGE
        # q = .5 * densityAtAltitude(convert(8000, "ft", "m")) * convert(180, "kts", "m/s") ** 2 # Dynamic prressure at cruise
        # Wpress = 0 # no pressurization weight penalty for our a/class
        # WfImperial = 0.052 * convert(Sf, "m^2", "ft^2")**1.086 * Nz*convert(Wdg, "N", "lb")**0.177 * convert(Lt, "m^2", "ft^2")**-0.051 * LD**-0.072 * convert(q, "N/m^2","lb/ft^2")**0.241 + Wpress # RAYMER eqn 15.48
        
        return convert(WfImperial, "lb", "N")

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

# class Wing(Surface):
#     span = None # number [m] : (0 <= x)
#     aspectRatio = None # number : (0 <= x)
#     chord = None # number [m] : (0 <= x)
#     Nz = None #FIXME do we use a different load factor? 3 or something?
#     sweep = None # number [deg] - wing sweep
#     lambd = None # number - wing taper ratio
#
#     @property
#     def weight(self):
#         Sw = WingPlanformArea(airplane)
#         Wdg = airplane.InitialGrossWeight
#         Wfw = 0.5 * airplane.powerplant.gas.mass
#         AR = span / chord
#         q = .5 * densityAtAltitude(cruiseAltitude) * convert(180, "knots", "m/s") ** 2 #Dynamic prressure at cruise
#         tc = airplane.thicknessToChord
#
#         Ww = 0.036*convert(Sw, "m^2", "ft^2")**0.758 * convert(Wfw, "N", "lb")**0.0035 * (AR / cosd(sweep)**2)**0.6 * convert(q, "N/m^2", "lb/ft^2")**0.006 * lambd**0.04 * (100 * tc / cosd(sweep))**-0.3 * (Nz * convert(Wdg, "n", "lb"))**0.49
#         return convert(Ww, "lb", "N")
#
# class HorizontalTail(component):
#     lambdaHT = None # horizontal tail taper ratio
#     sweepHT = None # number [deg] - sweep of horizontal tail
#     lambd = None # number - wing taper ratio
#
#     @property
#     def weight(self):
#         ch = 0.80 # horizontal tail volume coefficient
#         S = airplane.wing.span
#         c = airplane.wing.chord
#         dt = 0.5 * airplane.fuselage.length # FIXME just an estimation based on tecnam sizes
#         Sht = ch * (S * c / dt)
#         tc = airplane.thicknessToChord
#         AR = airplane.span / airplane.chord
#
#         Wht = 0.016 * (Nz*convert(Wdg, "n", "lb"))**0.414 * convert(q, "N/m^2", "lb/ft^2")**0.168 * convert(Sht, "m^2", "ft^2")**0.896 * (100 * tc / cosd(lambd))**-0.12 * (AR / cosd(sweepHT)**2)**0.043 * lambdHT**-0.02
#         return convert(Wht, "lb", "N")
#
# class VerticalTail(component):
#     lambdaVT = None # number - vertical tail taper ratio
#     sweepVT = None # number - sweep of vertical tail
#     Nz = None #FIXME do we use a different load factor? 3 or something?
#
#     @property
#     def weight(self):
#         HtHv = 0 # FOR CONVENTIONAL TAIL = 0.0, FOR T-TAIL = 1.0
#         Wdg = airplane.InitialGrossWeight
#         q = .5 * densityAtAltitude(convert(cruiseAltitude, "ft", "m")) * convert(180, "knots", "m/s") ** 2 #Dynamic prressure at cruise
#         cv = 0.07 # vertical tail volume coefficient for twin engine GA - RAYMER table 6.4
#         dv = 0.5 * airplane.fuselage.length # FIXME just an estimation based on Tecnam sizes
#         bw = airplane.wing.span # wingspan
#         Sw = WingPlanformArea(airplane) # wing area
#         Svt = cv * (Sw * bw / dv)#Vertical Tail area
#         tc = airplane.thicknessToChord
#         AR = airplane.span / airplane.chord
#
#         Wvt = 0.073 * (1 + 0.2*HtHv) * (Nz * convert(Wdg, "N", "lb"))**0.376 * convert(q, "N/m^2", "lb/ft^2")**0.122 * convert(Svt, "m^2", "ft^2")**0.873 * (100 * tc / cosd(sweepVT))**-0.49 * (AR / cosd(sweepVT)**2) * lambdaVT**0.039
#         return convert(Wvt, "lb", "N")
#
# class MainGear(component):
#     Lm = None # number [m] - length of main landing gear
#     Nland = 1 #FIXME ultimate load factor during landing
#
#     @property
#     def weight(self):
#         Wland = airplane.InitialGrossWeight # FIXME do we just use T/O weight in case of an early failure?
#
#         Wmg = 0.095 * (Nz * convert(Wland, "N", "lb"))**0.768 * (convert(Lm, "m", "in")/12)**0.409
#         return convert(Wmg, "lb", "N")
#
# class FrontGear(component):
#     Ln = None # number [m] - Length of nose landing gear
#     Nland = 1 #FIXME
#
#     @property
#     def weight(self):
#         Wland = airplane.InitialGrossWeight # FIXME
#
#         Wng = 0.125 * (Nl * convert(Wland, "N", "lb"))**0.566 * (convert(Ln, "m", "in") / 12)**0.845
#         return convert(Wng, "lb", "N")
#
# class InstalledEngine(component): # FIXME - IS THIS ACUTALLY GOING TO BE CONTAINED IN THE ENGINE OBJECT?
#     Weng = None # number [m] - weight of individual engine
#     Neng = len(airplane.engines) # number of engines
#
#     @property
#     def weight(self):
#         Weng = 2.575 * convert(Weng, "N", "lb")**0.922 * Neng
#
#         return convert(Weng, "lb", "N")
#
# class FuelSystem(component):
#     Vt = None # number [L] - total fuel volume
#     Vi = None # number [L] - total integral tanks volume (should be same as Vt as we have no drop tanks...or DO we??? O_o)
#     Nt = None # number of fuel tanks
#     Neng = len(airplane.engines) # number of engines
#
#     @property
#     def weight(self):
#         Wfs = 2.49 * convert(Vt, "L", "gal")**0.726 * (1 / (Vi/Vt))**0.363 * Nt**0.242 * Neng**0.157
#
#         return convert(Wfs, "lb", "N")
#
# class FlightControls(component):
#     Lfueselage = None # number [m] - FIXME fuselage length
#     span = None # number [m] : (0 <= x) - wingspan
#     Nz = None #FIXME do we use a different load factor? 3 or something?
#     Wdg = airplane.InitialGrossWeight #FIXME where do we pull the guess W0 from?
#
#     @property
#     def weight(self):
#         Wfc = 0.053 * convert(Lfueselage, "m", "ft")**1.536 * convert(span, "m", "ft")**0.371 * (Nz * convert(Wdg, "N", "lb") * 10**-4)**0.80
#
#         return convert(Wfc, "lb", "N")
#
# class Hydraulics(component):
#     Wdg = airplane.InitialGrossWeight
#
#     @property
#     def weight(self):
#         Whyd = 0.001 * Wdg # NO CONVERSION NECESSARY
#
#         return Whyd
#
# class Avionics(component):
#     Wuav = None # number [N] - weight of uninstalled avionics (typically 800-1400 lb or 3558 - 6227 N)
#
#     @property
#     def weight(self):
#         Wavi = 2.117 * convert(Wuav, "N", "lb")**0.933
#
#         return convert(Wavi, "lb". "N")
#
#
# class Electronics(component):
#     Wfs = airplane.FuelSystem.weight # Fuel system weight [N] (FIXME: IS THIS THE RIGHT CALL FORMAT?)
#     Wavi = airplane.Avionics.weight # Installed avionics weight [N] (FIXME: IS THIS THE RIGHT CALL FORMAT?)
#
#     @property
#     def weight(self):
#         Welec = 12.57 * (convert(Wfs, "N", "lb") + convert(Wavi, "N", "lb"))**0.51
#
#         return convert(Welec, "lb", "N")
#
# class AirConIce(component):
#     Wdg = airplane.InitialGrossWeight
#     Np = airplane.passengers + airplane.pilots
#     Wavi = airplane.Avionics.weight # FIXME is this the correct call?
#     M = None # FIXME - do we want to make a guess or just assume a value btw 0.23 and 0.28 (150-180 knots)
#
#     @property
#     def weight(self)
#         Wavi = 0.265 * convert(Wdg, "N", "lb")**0.52 * Np**0.68 * convert(Wavi, "N", "lb")**0.17 * M**0.08
#
#         return convert(Wavi, "lb", "N")
#
# class Furnishings(component):
#     Wdg = airplane.InitialGrossWeight
#
#     @property
#     def weight(self)
#         Wfurn = 0.0582 * convert(Wdg, "N", "lb") - 65
#
#         return convert(Wfurn, "lb", "N")
#
    
    
    

    
    
    maximumLiftCoefficient = None # number

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
        CLs = float(self.data["CL"])
        
        return max(CLs)
    
    # FIXME: not sure where this is supposed to go
    # span = None # number [m] : (0 <= x)
    # aspectRatio = None # number : (0 <= x)
    # chord = None # number [m] : (0 <= x)
    # Sw = WingPlanformArea(airplane)
    # Wdg = airplane.InitialGrossWeight
    # Wfw = 0.5 * airplane.powerplant.gas.mass
    # AR = span / chord
    # q = .5 * densityAtAltitude(convert(8000, "ft", "m")) * convert(180, "knots", "m/s") ** 2 #Dynamic prressure at cruise
    # tc = 0.12 # FIXME just used 12% t/c based on NACA ##12 series
    # Nz = 1 #FIXME do we use a different load factor? 3 or something?
    # @property
    # def weight(self):
    #     Ww = 0.036*convert(Sw, "m^2", "ft^2")**0.758 * convert(Wfw, "N", "lb")**0.0035 * AR**0.6 * convert(q, "N/m^2", "lb/ft^2")**0.006 * tc**-0.3 * (Nz * convert(Wdg, "n", "lb"))**0.49
    #     return convert(Ww, "lb", "N")

class Tail:
    horizontalStabilizer = None # Surface Object
    verticalStabilizer = None # Surface Object

# class HorizontalTail(component):
#     ch = 0.80 # horizontal tail volume coefficient
#     S = airplane.wing.span
#     c = airplane.wing.chord
#     dt = 0.5 * airplane.fuselage.length # FIXME just an estimation based on tecnam sizes
#     Sht = ch * (S * c / dt)
#     tc = 0.12 # FIXME just used 12% t/c based on NACA ##12 series
#     AR = airplane.span / airplane.chord
#     lambdah = 1 # FIXME Dunno what this is supposed to be
#     horizontalSweep = 0 # maybe we want sweep?
#     Wht = 0.016 * (Nz*convert(Wdg, "N", "lb"))**0.414 * q**0.168 * convert(Sht, "m^2", "ft^2")**0.896 * (100 * tc)**-0.12 * (AR / cos(HorizontalSweep)**2)**0.043 * lambdah**-0.02
#
#     return convert(Wht, "lb", "N") # FIXME: not sure what this return is doing here, but it isn't python
