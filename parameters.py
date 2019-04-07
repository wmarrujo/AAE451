from utilities import *
from csvTools import *
from convert import convert
from scipy import *
from stdatmo import * # standard atmospheric conditions
from constants import *

################################################################################

class Mission:
    segments = None
    
    def simulate(self, tstep, Airplane, recordingFunction):
        t = 0 # s
        iteration = 0
        recordingFunction(t, "Start", Airplane)
        
        for segment in self.segments:
            t0 = t
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
    name = None # string : name of the airplane (mostly so that we can name simulation files uniquely)
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
    density = None # number [kg/m^3] : (0 <= x)

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

class Engine(Component): # the engines/motors that drive the propeller
    maxPower = None # number [W] : (0 <= x)
    propeller = None # propeller object
    cost = None # number [USD] : (0 <= x)
    mass = None # number [kg] : (0 <= x) # uninstalled engine mass
    
    diameter = None # number [m] : (0 <= x)
    length = None # number [m] : (0 <= x)
    
    def __init__(self, interferenceFactor, diameter, length, uninstalledMass, numberOfEngines):
        self.interferenceFactor = interferenceFactor
        self.referenceLength = diameter
        self.diameter = diameter
        self.length = length
        self.mass = self.installedEngineMass(uninstalledMass, numberOfEngines)
    
    def installedEngineMass(self, uninstalledMass, numberOfEngines):
        WengImperial = 2.575 * convert(uninstalledMass, "N", "lb")**0.922 * numberOfEngines
        WengMetric = convert(WengImperial, "lb", "N")
        
        return WengMetric/g
    
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

class Fuselage(Component):
    diameter = None # number [m] : (0 <= x)
    length = None # number [m]
    
    def __init__(self, interferenceFactor, diameter, length, airplane):
        self.interferenceFactor = interferenceFactor
        self.referenceLength = diameter
        self.diameter = diameter
        self.length = length
        self.mass = self.calculateFuselageMass(airplane)
    
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
    
    def calculateFuselageMass(self, airplane):
        Sf = self.wettedArea
        Wdg = airplane.InitialGrossWeight #FIXME where do we pull the guess W0 from?
        Lt = 0.45*self.length #Based roughly on Tecnam Lt to L ratio
        LD = self.length / self.diameter #CHANGE FOR ELIPTICAL (or other) FUSELAGE
        q = .5 * densityAtAltitude(cruiseAltitude) * convert(180, "kts", "m/s") ** 2 #Dynamic pressure at cruise
        Wpress = 0 #no pressurization weight penalty for our a/class
        Nz = airplane.LoadFactor
        
        WfImperial = 0.052 * convert(Sf, "m^2", "ft^2")**1.086 * (Nz*convert(Wdg, "N", "lb"))**0.177 * convert(Lt, "m^2", "ft^2")**(-0.051) * LD**(-0.072) * convert(q, "N/m^2","lb/ft^2")**0.241 + Wpress #RAYMER eqn 15.48
        WfMetric = convert(WfImperial, "lb", "N")
        
        return WfMetric / g

class Surface(Component):
    planformArea = None # number [m^2] : (0 <= x)
    thicknessToChord = None # number : (0 <= x)
    airfoil = None # airfoil object
    sweep = None # IN RADIANS
    taper = None # taper ratio
    
    def __init__(self, interferenceFactor, planformArea, thicknessToChord, span, sweep, taper):
        self.interferenceFactor = interferenceFactor
        self.referenceLength = span
        self.thicknessToChord = thicknessToChord
        self.planformArea = planformArea
        self.sweep = sweep
        self.taper = taper
    
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
    
    def __init__(self, interferenceFactor, planformArea, thicknessToChord, span, sweep, taper, airplane):
        Surface.__init__(self, interferenceFactor, planformArea, thicknessToChord, span, sweep, taper)
        self.mass = self.calculateWingMass(airplane)
        
    def calculateWingMass(self, airplane):
        span = self.span # [m]
        aspectRatio = self.aspectRatio
        chord = self.chord # [m]
        Nz = airplane.LoadFactor
        sweep = self.sweep # number [deg] - wing sweep
        lambd = self.taper # number - wing taper ratio
        
        Sw = self.planformArea
        Wdg = airplane.InitialGrossWeight
        Wfw = 0.5 * airplane.powerplant.gas.mass
        AR = self.aspectRatio
        q = .5 * densityAtAltitude(cruiseAltitude) * convert(180, "kts", "m/s") ** 2 #Dynamic pressure at cruise
        tc = self.thicknessToChord

        Ww = 0.036*convert(Sw, "m^2", "ft^2")**0.758 * convert(Wfw, "N", "lb")**0.0035 * (AR / cos(sweep)**2)**0.6 * convert(q, "N/m^2", "lb/ft^2")**0.006 * lambd**0.04 * (100 * tc / cos(sweep))**-0.3 * (Nz * convert(Wdg, "N", "lb"))**0.49
        WwMetric = convert(Ww, "lb", "N")
        return WwMetric / g

class HorizontalStabilizer(Surface):

    def __init__(self, interferenceFactor, planformArea, thicknessToChord, span, sweep, taper, airplane):
        Surface.__init__(self, interferenceFactor, planformArea, thicknessToChord, span, sweep, taper)
        self.mass = self.calculateHorizontalTailMass(airplane)

    def calculateHorizontalTailMass(self, airplane):
        Wdg = airplane.InitialGrossWeight
        Nz = airplane.LoadFactor
        lambdHT = self.taper # horizontal tail taper ratio
        sweepHT = self.sweep # number [deg] - sweep of horizontal tail
        lambd = airplane.wing.taper # number - wing taper ratio
        ch = 0.80 # horizontal tail volume coefficient RAYMER/NOTES
        S = airplane.wing.span
        c = airplane.wing.chord
        dt = 0.5 * airplane.fuselage.length # FIXME just an estimation based on tecnam sizes, TODO: revisit when static margin stuff is done
        q = .5 * densityAtAltitude(convert(cruiseAltitude, "ft", "m")) * convert(180, "kts", "m/s") ** 2 #Dynamic prressure at cruise
        Sht = ch * (S * c / dt)
        tc = airplane.wing.thicknessToChord
        AR = airplane.wing.span / airplane.wing.chord

        WhtImperial = 0.016 * (Nz*convert(Wdg, "N", "lb"))**0.414 * convert(q, "N/m^2", "lb/ft^2")**0.168 * convert(Sht, "m^2", "ft^2")**0.896 * (100 * tc / cos(lambd))**-0.12 * (AR / cos(sweepHT)**2)**0.043 * lambdHT**-0.02
        WhtMetric = convert(WhtImperial, "lb", "N")
        return WhtMetric / g

class VerticalStabilizer(Surface):

    def __init__(self, interferenceFactor, planformArea, thicknessToChord, span, sweep, taper, airplane):
        Surface.__init__(self, interferenceFactor, planformArea, thicknessToChord, span, sweep, taper)
        self.mass = self.calculateVerticalTailMass(airplane)

    def calculateVerticalTailMass(self, airplane):
        lambdVT = self.taper # number - vertical tail taper ratio
        sweepVT = self.sweep # number - sweep of vertical tail
        Nz = airplane.LoadFactor #FIXME do we use a different load factor? 3 or something?
        HtHv = 0 # FOR CONVENTIONAL TAIL = 0.0, FOR T-TAIL = 1.0
        Wdg = airplane.InitialGrossWeight
        q = .5 * densityAtAltitude(convert(cruiseAltitude, "ft", "m")) * convert(180, "kts", "m/s") ** 2 #Dynamic prressure at cruise
        cv = 0.07 # vertical tail volume coefficient for twin engine GA - RAYMER table 6.4
        dv = 0.5 * airplane.fuselage.length # FIXME just an estimation based on Tecnam sizes
        bw = airplane.wing.span # wingspan
        Sw = airplane.wing.planformArea # wing area
        Svt = cv * (Sw * bw / dv)#Vertical Tail area
        tc = airplane.wing.thicknessToChord
        AR = airplane.wing.span / airplane.wing.chord

        WvtImperial = 0.073 * (1 + 0.2*HtHv) * (Nz * convert(Wdg, "N", "lb"))**0.376 * convert(q, "N/m^2", "lb/ft^2")**0.122 * convert(Svt, "m^2", "ft^2")**0.873 * (100 * tc / cos(sweepVT))**-0.49 * (AR / cos(sweepVT)**2) * lambdVT**0.039
        WvtMetric = convert(WvtImperial, "lb", "N")
        return WvtMetric / g

class MainGear(Component):
    landloadfactor = None
    gearlength = None
    
    def __init__(self, NLand, Lm, airplane):
        self.landloadfactor = NLand
        self.gearlength = Lm
        self.mass = self.calculateMainGearMass(airplane)
    
    def calculateMainGearMass(self, airplane):
        Wland = airplane.InitialGrossWeight # FIXME: do we just use T/O weight in case of an early failure?
        Nz = self.landloadfactor # FIXME: do we use a different load factor? 3 or something?
        Lm = self.gearlength
        
        WmgImperial = 0.095 * (Nz * convert(Wland, "N", "lb"))**0.768 * (convert(Lm, "m", "in")/12)**0.409
        WmgMetric = convert(WmgImperial, "lb", "N")
        return WmgMetric / g

class FrontGear(Component):
    landloadfactor = None
    gearlength = None
    
    def __init__(self, Nland, Ln, airplane):
        self.landloadfactor = Nland
        self.gearlength = Ln
        self.mass = self.calculateFrontGearMass(airplane)
        

    def calculateFrontGearMass(self, airplane):
        Wland = airplane.InitialGrossWeight # FIXME
        Nland = self.landloadfactor
        Ln = self.gearlength
        
        WngImperial = 0.125 * (Nland * convert(Wland, "N", "lb"))**0.566 * (convert(Ln, "m", "in") / 12)**0.845
        WngMetric = convert(WngImperial, "lb", "N")
        return WngMetric / g

class FuelSystem(Component):
    def __init__(self, airplane):
        self.mass = self.calculateFuelSystemMass(airplane)
        
    def calculateFuelSystemMass(self, airplane):
        if airplane.powerplant.gas: # make sure gas system exists
            Vt = airplane.powerplant.gas.mass / airplane.powerplant.gas.density # number [L] - total fuel volume
            Vi = Vt # number [L] - total integral tanks volume (should be same as Vt as we have no drop tanks...or DO we??? O_o)
            Nt = 2 # number of fuel tanks # FIXME: HARD NUM
            Neng = len(airplane.engines) # number of engines
            
            Wfs = 2.49 * convert(Vt, "L", "gal")**0.726 * (1 / (Vi/Vt))**0.363 * Nt**0.242 * Neng**0.157
            
            return convert(Wfs, "lb", "N")
        else:
            return 0 # TODO: implement for if no gas fuel system

class FlightControls(Component):
    def __init__(self, airplane):
        self.mass = self.calculateFlightControlsMass(airplane)
    
    def calculateFlightControlsMass(self, airplane):
        Lfueselage = airplane.fuselage.length # number [m]
        span = airplane.wing.span # number [m] : (0 <= x) - wingspan
        Nz = airplane.LoadFactor
        Wdg = airplane.InitialGrossWeight

        WfcImperial = 0.053 * convert(Lfueselage, "m", "ft")**1.536 * convert(span, "m", "ft")**0.371 * (Nz * convert(Wdg, "N", "lb") * 10**-4)**0.80
        WfcMetric = convert(WfcImperial, "lb", "N")
        return WfcMetric / g

class Hydraulics(Component):
    def __init__(self, airplane):
        self.mass = self.calculateHydraulicsMass(airplane)

    def calculateHydraulicsMass(self, airplane):
        Wdg = airplane.InitialGrossWeight
        Whyd = 0.001 * Wdg # NO CONVERSION NECESSARY

        return Whyd / g

class Avionics(Component):
    def __init__(self, Wuav):
        self.mass = self.calculateAvionicsMass(Wuav)

    def calculateAvionicsMass(self, Wuav):
        WuninAvi = Wuav # number [N] - weight of uninstalled avionics (typically 800-1400 lb or 3558 - 6227 N)

        WaviImperial = 2.117 * convert(Wuav, "N", "lb")**0.933
        WaviMetric = convert(WaviImperial, "lb", "N")
        return WaviMetric / g


class Electronics(Component):
    def __init__(self, airplane):
        self.mass = self.calculateElectronicsMass(airplane)

    def calculateElectronicsMass(self, airplane):
        Wfs = airplane.fuelSystem.mass * g # Fuel system weight [N] (FIXME: IS THIS THE RIGHT CALL FORMAT?)
        Wavi = airplane.avionics.mass * g # Installed avionics weight [N] (FIXME: IS THIS THE RIGHT CALL FORMAT?)

        WelecImperial = 12.57 * (convert(Wfs, "N", "lb") + convert(Wavi, "N", "lb"))**0.51
        WelecMetric = convert(WelecImperial, "lb", "N")
        return WelecMetric / g

class AirConIce(Component):
    def __init__(self, airplane):
        self.mass = self.calculateAirConIceMass(airplane)

    def calculateAirConIceMass(self, airplane):
        Wdg = airplane.InitialGrossWeight
        Np = airplane.passengers + airplane.pilots
        Wavi = airplane.avionics.mass * g # FIXME is this the correct call?
        M = convert(180, "kts", "m/s") / sqrt(γ * R * temperatureAtAltitude(cruiseAltitude)) # FIXME - do we want to make a guess or just assume a value btw 0.23 and 0.28 (150-180 kts)

        WaciImperial = 0.265 * convert(Wdg, "N", "lb")**0.52 * Np**0.68 * convert(Wavi, "N", "lb")**0.17 * M**0.08
        WaciMetric = convert(WaciImperial, "lb", "N")
        return WaciMetric / g

class Furnishings(Component):
    def __init__(self, airplane):
        self.mass = self.calculateFurnishingsMass(airplane)

    def calculateFurnishingsMass(self, airplane):
        Wdg = airplane.InitialGrossWeight
        Wfurn = 0.0582 * convert(Wdg, "N", "lb") - 65

        return convert(Wfurn, "lb", "N")







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
    # q = .5 * densityAtAltitude(convert(8000, "ft", "m")) * convert(180, "kts", "m/s") ** 2 #Dynamic prressure at cruise
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
