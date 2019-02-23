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
class Segment:
    velocity = None
    range = None
    time = None

class Airplane:
    etap = None
    thrust = None
    power = None
    velocity = None
    Cbhp = None
    propellerRotationSpeed = None
    propellerDiameter = None
    takeoffWeight = None