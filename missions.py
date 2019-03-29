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
    Segment("startup"),
    Segment("takeoff"),
    Segment("climb"),
    # Segment("cruise"),
    # Segment("descent"),
    # Segment("abortClimb"),
    # Segment("loiter"),
    # Segment("abortDescent"),
    # Segment("landing"),
    # Segment("shutdown")
    ])

# STARTUP

def _designMissionInitializeStartup(airplane, t, t0):
    airplane.throttle = 0.3
    airplane.position = 0
    airplane.pitch = 0
    airplane.flightPathAngle = 0

def _designMissionCompletedStartup(airplane, t, t0):
    return convert(10, "min", "s") <= t - t0

def _designMissionUpdateStartup(airplane, t, tstep):
    UpdateFuel(airplane, tstep)

designMission.segments["startup"].initialize = _designMissionInitializeStartup
designMission.segments["startup"].completed = _designMissionCompletedStartup
designMission.segments["startup"].update = _designMissionUpdateStartup

# TAKEOFF

def _designMissionInitializeTakeoff(airplane, t, t0):
    airplane.throttle = 1

def _designMissionCompletedTakeoff(airplane, t, t0):
    return TakeoffSpeed(airplane) <= airplane.speed

def _designMissionUpdateTakeoff(airplane, t, tstep):
    # see Raymer-v6 section 17.8.1 
    acceleration = AccelerationOnGround(airplane) # find acceleration from thrust, drag and ground friction
    airplane.speed += acceleration * tstep # update speed with acceleration
    airplane.position += airplane.speed * tstep # update position with speed
    UpdateFuel(airplane, tstep) # update the fuel

designMission.segments["takeoff"].initialize = _designMissionInitializeTakeoff
designMission.segments["takeoff"].completed = _designMissionCompletedTakeoff
designMission.segments["takeoff"].update = _designMissionUpdateTakeoff

# CLIMB

def _designMissionInitializeClimb(airplane, t, t0):
    airplane.throttle = 1

def _designMissionCompletedClimb(airplane, t, t0):
    return cruiseAltitude <= airplane.altitude

def _designMissionUpdateClimb(airplane, t, tstep):
    a = MaximumLiftOverDragAngleOfAttack(airplane)
    T = AirplaneThrust(airplane)
    D = AirplaneDrag(airplane)
    W = AirplaneWeight(airplane)
    
    airplane.pitch = arcsin((T-D)/W)
    airplane.flightPathAngle = airplane.pitch - a/2 # FIXME: this is a hack, please figure out what this actually should be
    airplane.altitude += airplane.speed * sin(airplane.flightPathAngle) * tstep
    airplane.position += airplane.speed * cos(airplane.flightPathAngle) * tstep
    UpdateFuel(airplane, tstep)

designMission.segments["climb"].initialize = _designMissionInitializeClimb
designMission.segments["climb"].completed = _designMissionCompletedClimb
designMission.segments["climb"].update = _designMissionUpdateClimb

# # CRUISE
# 
# def _designMissionInitializeCruise(airplane, t, t0):
#     airplane.altitude = cruiseAltitude
#     airplane.speed = convert(200, "kts", "m/s")
# 
# def _designMissionCompletedCruise(airplane, t, t0):
#     return airplane.range <= convert(300, "nmi", "m")
# 
# def _designMissionUpdateCruise(airplane, t, tstep):
#     pass
#     # use constant CL strategy in Raymer to get level flight
#
# designMission.segments["cruise"].initialize = _designMissionInitializeCruise
# designMission.segments["cruise"].completed = _designMissionCompletedCruise
# designMission.segments["cruise"].update = _designMissionUpdateCruise
#
# # DESCENT
# 
# def _designMissionInitializeDescent(airplane, t, t0):
#     airplane.throttle = 0.3
# 
# def _designMissionCompletedDescent(airplane, t, t0):
#     return airplane.altitude <= obstacleHeight
# 
# def _designMissionUpdateDescent(airplane, t, tstep):
#     pass
#
# designMission.segments["descent"].initialize = _designMissionInitializeDescent
# designMission.segments["descent"].completed = _designMissionCompletedDescent
# designMission.segments["descent"].update = _designMissionUpdateDescent
#
# # ABORT CLIMB
# 
# def _designMissionInitializeAbortClimb(airplane, t, t0):
#     airplane.throttle = 1
# 
# def _designMissionCompletedAbortClimb(airplane, t, t0):
#     return loiterAltitude <= airplane.altitude
# 
# def _designMissionUpdateAbortClimb(airplane, t, tstep):
#     pass
#
# designMission.segments["abortClimb"].initialize = _designMissionInitializeAbortClimb
# designMission.segments["abortClimb"].completed = _designMissionCompletedAbortClimb
# designMission.segments["abortClimb"].update = _designMissionUpdateAbortClimb
#
# # LOITER
# 
# def _designMissionInitializeLoiter(airplane, t, t0):
#     airplane.throttle = 0.6
# 
# def _designMissionCompletedLoiter(airplane, t, t0):
#     return loiterTime <= t - t0
# 
# def _designMissionUpdateLoiter(airplane, t, tstep):
#     pass
#     # use constant CL strategy in Raymer to get level flight
#
# designMission.segments["loiter"].initialize = _designMissionInitializeLoiter
# designMission.segments["loiter"].completed = _designMissionCompletedLoiter
# designMission.segments["loiter"].update = _designMissionUpdateLoiter
#
# # ABORT DESCENT
# 
# def _designMissionInitializeAbortDescent(airplane, t, t0):
#     airplane.throttle = 0.3
# 
# def _designMissionCompletedAbortDescent(airplane, t, t0):
#     return airplane.altitude <= obstacleHeight
# 
# def _designMissionUpdateAbortDescent(airplane, t, tstep):
#     pass
#
# designMission.segments["abortDescent"].initialize = _designMissionInitializeAbortDescent
# designMission.segments["abortDescent"].completed = _designMissionCompletedAbortDescent
# designMission.segments["abortDescent"].update = _designMissionUpdateAbortDescent
#
# # LANDING
# 
# def _designMissionInitializeLanding(Airplane, t, t0):
#     Airplane.altitude = obstacleHeight
#     Airplane.throttle = 0.1
# 
# def _designMissionCompletedLanding(Airplane, t, t0):
#     return Airplane.speed == 0
# 
# def _designMissionUpdateLanding(Airplane, t, tstep):
#     # see Raymer-v6 section 17.8.1
#     acceleration = accelerationOnGroundLanding(Airplane) # find acceleration from thrust, drag and ground friction
#     airplane.speed += acceleration * tstep # update speed with acceleration
#     airplane.position += airplane.speed * tstep # update position with speed
#     updateFuel(Airplane) # update the fuel
# 
# designMission.segments["landing"].initialize = _designMissionInitializeLanding
# designMission.segments["landing"].completed = _designMissionCompletedLanding
# designMission.segments["landing"].update = _designMissionUpdateLanding

# # SHUTDOWN
#
# def _designMissionInitializeShutdown(Airplane, t, t0):
#     Airplane.throttle = 0.1
#
# def _designMissionCompletedShutdown(Airplane, t, t0):
#     return convert(10, "min", "s") <= t - t0
#
# def _designMissionUpdateShutdown(Airplane, t, tstep):
#     pass
#
# designMission.segments["shutdown"].initialize = _designMissionInitializeShutdown
# designMission.segments["shutdown"].completed = _designMissionCompletedShutdown
# designMission.segments["shutdown"].update = _designMissionUpdateShutdown

# REFERENCE MISSION

referenceMission = Mission()
referenceMission.passengers = 3
referenceMission.pilots = 1
