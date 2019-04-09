from utilities import *
from constants import *

from scipy import *

################################################################################

class Mission:
    segments = None
    
    def simulate(self, tstep, airplane, recordingFunction=(lambda t, s, a: None)):
        """
        takes a time step, an airplane definition, and an optional recording function to run each iteration
        returns the success of the simulation. If it was able to complete it, it returns True, if it encountered something that broke the verification, it returns False
        
        the recording function takes the simulation time, the segment name, and the airplane in its current state
        """
        
        t = 0 # s
        iteration = 0
        verified = verifySimulation(iteration, t, "Start", airplane)
        recordingFunction(t, "Start", airplane)
        print("Simulating {} ".format(airplane.name), end="", flush="True")
        
        for segment in self.segments:
            t0 = t
            segment.initialize(airplane, t, t0)
            
            while verified and not segment.completed(airplane, t, t0):
                segment.update(airplane, t, tstep)
                recordingFunction(t, segment.name, airplane)
                
                t = t + tstep
                iteration += 1
                
                verified = verifySimulation(iteration, t, segment.name, airplane) # here to make sure the simulation doesn't run forever
                
                if iteration % 100 == 0:
                    print(".", end="", flush="True")
        
        print(" DONE - {}".format("succeeded" if verified else "failed"))
        return verified

def verifySimulation(iteration, t, segmentName, airplane):
    if iterationCap <= iteration:
        print("WARNING: simulation iteration cap reached")
        return False
    if timeCap <= t:
        print("WARNING: simulation time cap reached")
        return False
    return True

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
    pitch = None # number [rad]
    flightPathAngle = None # number [rad]
    wing = None # wing component object
    engines = [] # [engine object] # list of engines on airplane
    powerplant = None # powerplant object
    components = [] # [component objects] # list of components making up airplane (including wing)
    oswaldEfficiencyFactor = None # number : (0.7 < x < 0.85) # TODO: get better estimate
    compressibilityDragCoefficient = 0 # number : (0 = x) # we fly too slow
    miscellaneousParasiteDragFactor = None # number : (0 <= x)
    initialGrossWeight = None # number : initial guess for gross weight, changes with iterations
    productionQuantityNeeded = None  # number [planes] : (0 <= x)
    numberFlightTestAircraft = None  # number [planes] : (2 <= x <= 6)  # Raymer v6 18.4.2
    avionicsCost = None  # number [USD] : (0 <= x)
    horizontalStabilizer = None # HorizontalStabilizer object
    verticalStabilizer = None # VerticalStabilizer object
    
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
    
    @fuelMass.setter
    def fuelMass(self, m):
        edg = self.gas.energyDensity if self.gas else 0
        edb = self.battery.energyDensity if self.battery else 0
        p = self.percentElectric
        
        if 0 < p and p < 1: # hybrid
            self.gas.mass = m*edb*(1-p) / (edg*p + edb*(1-p))
            self.battery.mass = m*edg*p / (edb*(1-p) + edg*p)
        if p == 0: # fully gas
            self.gas.mass = m
        if p == 1: # fully battery
            self.battery.mass = m
    
    @property
    def emptyFuelMass(self):
        mb = self.battery.mass if self.battery is not None else 0 # TODO: approximation that battery mass is constant with charge & stuff
        
        return mb

class Gas:
    mass = None # number [kg] : (0 <= x)
    energyDensity = None # number [J/kg] : (0 <= x)
    density = None # number [kg/m^3] : (0 <= x)

class Battery:
    mass = None # number [kg] : (0 <= x)
    energyDensity = None # number [W*h/kg] : (0 <= x)
    capacity = None # number [J] : (0 <= x)
    charge = None # number : (0 <= x <= 1)
    
    @property
    def energy(self):
        E = self.capacity
        C = self.charge
        
        return E*C

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
    
    def setPlanformAreaWhileMaintainingAspectRatio(self, S):
        AR = self.aspectRatio
        self.planformArea = S
        self.span = sqrt(AR * S) # set the span
    
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
        
        return b**2/S
    
    @property
    def span(self):
        return self.referenceLength
    @span.setter
    def span(self, b):
        self.referenceLength = b
    
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
    
    def __init__(self, NLand, Lm, airplane):
        self.landloadfactor = NLand
        self.gearLength = Lm
        self.mass = self.calculateMainGearMass(airplane)
        
        # FIXME: all of these are hard-coded to nothing because we don't have a relationship for them yet
        self.formFactor = 0
        self.interferenceFactor = 1
        self.wettedArea = 0
    
    def calculateMainGearMass(self, airplane):
        Wland = airplane.InitialGrossWeight # FIXME: do we just use T/O weight in case of an early failure?
        Nz = self.landloadfactor # FIXME: do we use a different load factor? 3 or something?
        Lm = self.gearLength
        
        WmgImperial = 0.095 * (Nz * convert(Wland, "N", "lb"))**0.768 * (convert(Lm, "m", "in")/12)**0.409
        WmgMetric = convert(WmgImperial, "lb", "N")
        return WmgMetric / g
    
    @property
    def gearLength(self):
        return self.referenceLength
    @gearLength.setter
    def gearLength(self, length):
        self.referenceLength = length

class FrontGear(Component):
    landloadfactor = None
    
    def __init__(self, Nland, Ln, airplane):
        self.landloadfactor = Nland
        self.gearLength = Ln
        self.mass = self.calculateFrontGearMass(airplane)
        
        # FIXME: all of these are hard-coded to nothing because we don't have a relationship for them yet
        self.formFactor = 0
        self.interferenceFactor = 1
        self.wettedArea = 0

    def calculateFrontGearMass(self, airplane):
        Wland = airplane.InitialGrossWeight # FIXME
        Nland = self.landloadfactor
        Ln = self.gearLength
        
        WngImperial = 0.125 * (Nland * convert(Wland, "N", "lb"))**0.566 * (convert(Ln, "m", "in") / 12)**0.845
        WngMetric = convert(WngImperial, "lb", "N")
        return WngMetric / g
    
    @property
    def gearLength(self):
        return self.referenceLength
    @gearLength.setter
    def gearLength(self, length):
        self.referenceLength = length

class FuelSystem(Component):
    def __init__(self, airplane):
        self.mass = self.calculateFuelSystemMass(airplane)
        
        # FIXME: all of these are hard-coded to nothing because it doesn't contribute to drag right?
        self.formFactor = 0
        self.interferenceFactor = 1
        self.wettedArea = 0
        self.referenceLength = 0
        
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
        
        # FIXME: all of these are hard-coded to nothing because it doesn't contribute to drag right?
        self.formFactor = 0
        self.interferenceFactor = 1
        self.wettedArea = 0
        self.referenceLength = 0
    
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
        
        # FIXME: all of these are hard-coded to nothing because it doesn't contribute to drag right?
        self.formFactor = 0
        self.interferenceFactor = 1
        self.wettedArea = 0
        self.referenceLength = 0

    def calculateHydraulicsMass(self, airplane):
        Wdg = airplane.InitialGrossWeight
        Whyd = 0.001 * Wdg # NO CONVERSION NECESSARY

        return Whyd / g

class Avionics(Component):
    def __init__(self, Wuav):
        self.mass = self.calculateAvionicsMass(Wuav)
        
        # FIXME: all of these are hard-coded to nothing because it doesn't contribute to drag right?
        self.formFactor = 0
        self.interferenceFactor = 1
        self.wettedArea = 0
        self.referenceLength = 0

    def calculateAvionicsMass(self, Wuav):
        WuninAvi = Wuav # number [N] - weight of uninstalled avionics (typically 800-1400 lb or 3558 - 6227 N)

        WaviImperial = 2.117 * convert(Wuav, "N", "lb")**0.933
        WaviMetric = convert(WaviImperial, "lb", "N")
        return WaviMetric / g


class Electronics(Component):
    def __init__(self, airplane):
        self.mass = self.calculateElectronicsMass(airplane)
        
        # FIXME: all of these are hard-coded to nothing because it doesn't contribute to drag right?
        self.formFactor = 0
        self.interferenceFactor = 1
        self.wettedArea = 0
        self.referenceLength = 0

    def calculateElectronicsMass(self, airplane):
        Wfs = airplane.fuelSystem.mass * g # Fuel system weight [N] (FIXME: IS THIS THE RIGHT CALL FORMAT?)
        Wavi = airplane.avionics.mass * g # Installed avionics weight [N] (FIXME: IS THIS THE RIGHT CALL FORMAT?)

        WelecImperial = 12.57 * (convert(Wfs, "N", "lb") + convert(Wavi, "N", "lb"))**0.51
        WelecMetric = convert(WelecImperial, "lb", "N")
        return WelecMetric / g

class AirConIce(Component):
    def __init__(self, airplane):
        self.mass = self.calculateAirConIceMass(airplane)
        
        # FIXME: all of these are hard-coded to nothing because it doesn't contribute to drag right?
        self.formFactor = 0
        self.interferenceFactor = 1
        self.wettedArea = 0
        self.referenceLength = 0

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
        
        # FIXME: all of these are hard-coded to nothing because it doesn't contribute to drag right?
        self.formFactor = 0
        self.interferenceFactor = 1
        self.wettedArea = 0
        self.referenceLength = 0

    def calculateFurnishingsMass(self, airplane):
        Wdg = airplane.InitialGrossWeight
        Wfurn = 0.0582 * convert(Wdg, "N", "lb") - 65

        return convert(Wfurn, "lb", "N")

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