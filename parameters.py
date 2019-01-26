from convert import convert

class Mission:
    range = 0 # m
    loiter = 0 # s
    passengers = 1 #
    passengerWeight = 0 # N
    baggageWeight = 0 # N
    cruiseAltitude = 0 # m
    loiterAltitude = 0 # m
    
    def __str__(self):
        str =  "range:              {0}nmi\n".format(convert(self.range, "m", "nmi"))
        str += "loiter:             {0}hr".format(convert(self.loiter, "s", "hr"))
        str += "passengers:         {0}".format(self.passengers)
        str += "payload weight:     {0}lb".format(convert(self.passengers * self.passengerWeight + self.baggageWeight, "N", "lb"))
        str += "cruise altitude:    {0}ft".format(convert(self.cruiseAltitude, "m", "ft"))
        str += "loiter altitude:    {0}ft".format(convert(self.loiterAltitude, "m", "ft"))
        return str
    def __repr__(self):
        return self.__str__()

class Airplane:
    power = 0 # W
    emptyWeight = 0 # kg
    grossWeight = 0 # kg
    cruiseSpeed = 0 # m/s
    maxLoadFactor = 1 #
    wingspan = 0 # m
    tipChord = 0 # m
    rootChord = 0 # m
    CD0 = 0 #  # Parasite Drag Coefficient
    fuselageDiameter = 0 # m
    wing = None # Airfoil object
    powerplant = None # Powerplant object
    engines = 1 #  # number of engines
    propeller = None # Propeller Object
    fuel = None # Fuel Object

# SubSections

class Wing:
    sweep = 0 # rad
    rootChord = 0 # m
    tipChord = 0 # m
    span = 0 # m
    airfoil = None # Airfoil object
    
    @property
    def taperRatio(self):
        return self.tipChord / self.rootChord
    
    @property
    def meanAerodynamicChord(self):
        return (2/3) * self.rootChord * (1 + self.taperRatio + self.taperRatio**2) / (1 + self.taperRatio)
    
    @property
    def aspectRatio(self):
        return self.span / self.meanAerodynamicChord
    
    @property
    def oswaldEfficiency(self):
        return 1.78 * (1 - 0.045 * self.aspectRatio**0.68) - 0.64

class Airfoil:
    CLMax = 0 #
    thickness = 0 #

class Powerplant:
    rotationRate = 0 # rad/s
    efficiency = 1 #

class Propeller:
    efficiency = 1 #

class Fuel:
    pass

# Subsection Instances

