# LOCAL DEPENDENCIES

from utilities import *

from constants import *
from parameters import *
from equations import *

################################################################################
# MISSION
################################################################################

# DESIGN MISSION

designMission = Mission()
designMission.passengers = 5
designMission.pilots = 1

designMission.segments = Segments([
    Segment("startup"),
    Segment("takeoff"),
    Segment("climb"),
    Segment("cruise"),
    Segment("descent"),
    Segment("abortClimb"),
    Segment("loiter"),
    Segment("abortDescent"),
    Segment("landing"),
    Segment("shutdown")
    ])

# STARTUP

def _designMissionInitializeStartup(airplane, t, t0):
    airplane.throttle = 0.3
    airplane.position = 0
    airplane.pitch = 0
    airplane.flightPathAngle = 0

def _designMissionCompletedStartup(airplane, t, t0):
    return convert(10, "min", "s") <= t - t0

designMission.segments["startup"].initialize = _designMissionInitializeStartup
designMission.segments["startup"].completed = _designMissionCompletedStartup
designMission.segments["startup"].update = UpdateWaiting

# TAKEOFF

def _designMissionInitializeTakeoff(airplane, t, t0):
    airplane.throttle = 1

def _designMissionCompletedTakeoff(airplane, t, t0):
    return TakeoffSpeed(airplane) <= airplane.speed

designMission.segments["takeoff"].initialize = _designMissionInitializeTakeoff
designMission.segments["takeoff"].completed = _designMissionCompletedTakeoff
designMission.segments["takeoff"].update = UpdateTakeoff

# CLIMB

def _designMissionInitializeClimb(airplane, t, t0):
    airplane.throttle = 1

def _designMissionCompletedClimb(airplane, t, t0):
    return cruiseAltitude <= airplane.altitude

designMission.segments["climb"].initialize = _designMissionInitializeClimb
designMission.segments["climb"].completed = _designMissionCompletedClimb
designMission.segments["climb"].update = UpdateClimb

# CRUISE

def _designMissionInitializeCruise(airplane, t, t0):
    airplane.flightPathAngle = 0 # level flight
    airplane.pitch = 0 # angle of attack to maintain
    airplane.throttle = 0.7

def _designMissionCompletedCruise(airplane, t, t0):
    return convert(300, "nmi", "m") <= airplane.position

designMission.segments["cruise"].initialize = _designMissionInitializeCruise
designMission.segments["cruise"].completed = _designMissionCompletedCruise
designMission.segments["cruise"].update = UpdateCruise

# DESCENT

def _designMissionInitializeDescent(airplane, t, t0):
    airplane.throttle = 0

def _designMissionCompletedDescent(airplane, t, t0):
    return airplane.altitude <= convert(100, "ft", "m")

designMission.segments["descent"].initialize = _designMissionInitializeDescent
designMission.segments["descent"].completed = _designMissionCompletedDescent
designMission.segments["descent"].update = UpdateDescent

# ABORT CLIMB

def _designMissionInitializeAbortClimb(airplane, t, t0):
    airplane.throttle = 1
    airplane.speed = convert(75, "kts", "m/s")
    # airplane.altitude = 0 # set for condition in descent
    # TODO: figure out why still descending

def _designMissionCompletedAbortClimb(airplane, t, t0):
    return loiterAltitude <= airplane.altitude

designMission.segments["abortClimb"].initialize = _designMissionInitializeAbortClimb
designMission.segments["abortClimb"].completed = _designMissionCompletedAbortClimb
designMission.segments["abortClimb"].update = UpdateClimb

# LOITER

def _designMissionInitializeLoiter(airplane, t, t0):
    # TODO: initialize properly
    airplane.throttle = 0.6
    airplane.flightPathAngle = 0
    airplane.pitch = 0
    airplane.speed = MaximumLiftOverDragVelocity(airplane) # speed to maintain

def _designMissionCompletedLoiter(airplane, t, t0):
    return loiterTime <= t - t0

designMission.segments["loiter"].initialize = _designMissionInitializeLoiter
designMission.segments["loiter"].completed = _designMissionCompletedLoiter
designMission.segments["loiter"].update = UpdateCruise

# ABORT DESCENT

def _designMissionInitializeAbortDescent(airplane, t, t0):
    airplane.throttle = 0.3
    airplane.speed = convert(170, "kts", "m/s") # TODO: fix in same vein as with cruise velocity

def _designMissionCompletedAbortDescent(airplane, t, t0):
    return airplane.altitude <= 0

designMission.segments["abortDescent"].initialize = _designMissionInitializeAbortDescent
designMission.segments["abortDescent"].completed = _designMissionCompletedAbortDescent
designMission.segments["abortDescent"].update = UpdateDescent

# LANDING

def _designMissionInitializeLanding(airplane, t, t0):
    airplane.pitch = 0
    airplane.flightPathAngle = 0
    airplane.altitude = 0
    airplane.throttle = 0

def _designMissionCompletedLanding(airplane, t, t0):
    return airplane.speed <= 0.1

designMission.segments["landing"].initialize = _designMissionInitializeLanding
designMission.segments["landing"].completed = _designMissionCompletedLanding
designMission.segments["landing"].update = UpdateLanding

# SHUTDOWN

def _designMissionInitializeShutdown(airplane, t, t0):
    airplane.speed = 0
    airplane.throttle = 0.1

def _designMissionCompletedShutdown(airplane, t, t0):
    return convert(10, "min", "s") <= t - t0

designMission.segments["shutdown"].initialize = _designMissionInitializeShutdown
designMission.segments["shutdown"].completed = _designMissionCompletedShutdown
designMission.segments["shutdown"].update = UpdateWaiting