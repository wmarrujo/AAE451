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
    powerplant = None #motors & stuff

class Powerplant:
    eta = None
    engines = None
    maxPower = None
    def fuelUsedForEnergyUsed(missionSegment, energyUsed):
        pass
    propeller = None

class Propeller:
    eta
