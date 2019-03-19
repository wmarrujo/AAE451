from convert import convert
from parameters import *
from constants import *
from equations import *

################################################################################
# MISSION
################################################################################

# DESIGN MISSION

designMission = Mission()
designMission.passengers = 5
designMission.pilots = 1

designMission.segments = Segments([
    Segment("startup")#,
    # Segment("takeoff"),
    # Segment("climb"),
    # Segment("cruise"),
    # Segment("descent"),
    # Segment("abortClimb"),
    # Segment("loiter"),
    # Segment("abortDescent"),
    # Segment("landing"),
    # Segment("shutdown")
    ])

def _designMissionInitializeStartup(Airplane, t, t0):
    Airplane.throttle = 0.1
    Airplane.position = 0
def _designMissionCompletedStartup(Airplane, t, t0):
    return convert(10, "min", "s") <= t - t0
def _designMissionUpdateStartup(Airplane, t, tstep):
    runEngine(Airplane, tstep)
    # figure out how much fuel is used per time running at certain power
    # subtract fuel used
designMission.segments["startup"].initialize = _designMissionInitializeStartup
designMission.segments["startup"].completed = _designMissionCompletedStartup
designMission.segments["startup"].update = _designMissionUpdateStartup

def _designMissionInitializeTakeoff(Airplane, t, t0):
    Airplane.throttle = 1
    Airplane.position = 0
def _designMissionCompletedTakeoff(Airplane, t, t0):
    return takeoffSpeed <= Airplane.speed
def _designMissionUpdateTakeoff(Airplane, t, tstep):
    pass
    # see Raymer-v6 section 17.8.1 
    # find thrust
    # find acceleration from thrust, drag and ground friction
    # update speed with acceleration
    # update position with speed
designMission.segments["takeoff"].initialize = _designMissionInitializeTakeoff
designMission.segments["takeoff"].completed = _designMissionCompletedTakeoff
designMission.segments["takeoff"].update = _designMissionUpdateTakeoff

def _designMissionInitializeClimb(Airplane, t, t0):
    Airplane.throttle = 1
def _designMissionCompletedClimb(Airplane, t, t0):
    return cruiseAltitude <= Airplane.altitude
def _designMissionUpdateClimb(Airplane, t, tstep):
    Airplane.altitude = Airplane.altitude + climbAltitudeCredit(Airplane, tstep)
    Airplane.position = Airplane.position + climbPositionCredit(Airplane, tstep)
    Airplane.speed = climbVelocity(Airplane)
    
designMission.segments["climb"].initialize = _designMissionInitializeClimb
designMission.segments["climb"].completed = _designMissionCompletedClimb
designMission.segments["climb"].update = _designMissionUpdateClimb

def _designMissionInitializeCruise(Airplane, t, t0):
    Airplane.altitude = cruiseAltitude
    Airplane.speed = convert(200, "kts", "m/s")
def _designMissionCompletedCruise(Airplane, t, t0):
    return Airplane.range <= convert(300, "nmi", "m")
def _designMissionUpdateCruise(Airplane, t, tstep):
    pass
    # use constant CL strategy in Raymer to get level flight
designMission.segments["cruise"].initialize = _designMissionInitializeCruise
designMission.segments["cruise"].completed = _designMissionCompletedCruise
designMission.segments["cruise"].update = _designMissionUpdateCruise

def _designMissionInitializeDescent(Airplane, t, t0):
    Airplane.throttle = 0.3
def _designMissionCompletedDescent(Airplane, t, t0):
    return Airplane.altitude <= obstacleHeight
def _designMissionUpdateDescent(Airplane, t, tstep):
    pass
    # 
designMission.segments["descent"].initialize = _designMissionInitializeDescent
designMission.segments["descent"].completed = _designMissionCompletedDescent
designMission.segments["descent"].update = _designMissionUpdateDescent

def _designMissionInitializeAbortClimb(Airplane, t, t0):
    Airplane.throttle = 1
def _designMissionCompletedAbortClimb(Airplane, t, t0):
    return loiterAltitude <= Airplane.altitude
def _designMissionUpdateAbortClimb(Airplane, t, tstep):
    pass
    # 
designMission.segments["abortClimb"].initialize = _designMissionInitializeAbortClimb
designMission.segments["abortClimb"].completed = _designMissionCompletedAbortClimb
designMission.segments["abortClimb"].update = _designMissionUpdateAbortClimb

def _designMissionInitializeLoiter(Airplane, t, t0):
    Airplane.throttle = 0.6
def _designMissionCompletedLoiter(Airplane, t, t0):
    return loiterTime <= t - t0
def _designMissionUpdateLoiter(Airplane, t, tstep):
    pass
    # use constant CL strategy in Raymer to get level flight
designMission.segments["loiter"].initialize = _designMissionInitializeLoiter
designMission.segments["loiter"].completed = _designMissionCompletedLoiter
designMission.segments["loiter"].update = _designMissionUpdateLoiter

def _designMissionInitializeAbortDescent(Airplane, t, t0):
    Airplane.throttle = 0.3
def _designMissionCompletedAbortDescent(Airplane, t, t0):
    return Airplane.altitude <= obstacleHeight
def _designMissionUpdateAbortDescent(Airplane, t, tstep):
    pass
    # 
designMission.segments["abortDescent"].initialize = _designMissionInitializeAbortDescent
designMission.segments["abortDescent"].completed = _designMissionCompletedAbortDescent
designMission.segments["abortDescent"].update = _designMissionUpdateAbortDescent

def _designMissionInitializeLanding(Airplane, t, t0):
    Airplane.altitude = obstacleHeight
    Airplane.throttle = 0.1
def _designMissionCompletedLanding(Airplane, t, t0):
    return Airplane.speed == 0
def _designMissionUpdateLanding(Airplane, t, tstep):
    pass
    # 
designMission.segments["landing"].initialize = _designMissionInitializeLanding
designMission.segments["landing"].completed = _designMissionCompletedLanding
designMission.segments["landing"].update = _designMissionUpdateLanding

def _designMissionInitializeShutdown(Airplane, t, t0):
    Airplane.throttle = 0.1
def _designMissionCompletedShutdown(Airplane, t, t0):
    return convert(10, "min", "s") <= t - t0
def _designMissionUpdateShutdown(Airplane, t, tstep):
    pass
    # 
designMission.segments["shutdown"].initialize = _designMissionInitializeShutdown
designMission.segments["shutdown"].completed = _designMissionCompletedShutdown
designMission.segments["shutdown"].update = _designMissionUpdateShutdown

# REFERENCE MISSION

referenceMission = Mission()
referenceMission.passengers = 3
referenceMission.pilots = 1
