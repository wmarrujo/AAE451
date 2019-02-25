from convert import convert

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
        "shutdown": {}}
    segments = ["takeoff", "climb", "cruise", "descent", "abortClimb", "loiter", "abortDescent", "landing", "shutdown"]

class FlightCondition: # for simulation
    altitude = None
    speed = None
    powerSetting = None
    weight = None # complete airplane weight
    angleOfAttack = None

class Airplane:
    etap = None
    thrust = None
    power = None
    velocity = None
    Cbhp = None
    propellerRotationSpeed = None
    propellerDiameter = None
    takeoffWeight = None
    powerplant = None # motors & stuff

class Powerplant:
    propeller = None # propeller object
    engines = None # number of engines
    engine = None # engine object

class Propeller:
    eta = None # number or function that calculates number based on flight conditions

class Engine:
    fuelSource = None # Fuel Object

class Fuel:
    pass

class Battery(Fuel):
    pass

class Gas(Fuel):
    pass