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
    # TODO: maybe set this to max L/D velocity, then hold that? (using max excess power Velocity)

def _designMissionCompletedClimb(airplane, t, t0):
    return cruiseAltitude <= airplane.altitude

def _designMissionUpdateClimb(airplane, t, tstep):
    a = MaximumLiftOverDragAngleOfAttack(airplane) # DEBUG: something's wrong with descent
    T = AirplaneThrust(airplane)
    D = AirplaneDrag(airplane)
    W = AirplaneWeight(airplane)
    
    airplane.flightPathAngle = arcsin((T-D)/W)
    airplane.pitch = airplane.flightPathAngle + a
    airplane.altitude += airplane.speed * sin(airplane.flightPathAngle) * tstep
    airplane.position += airplane.speed * cos(airplane.flightPathAngle) * tstep
    UpdateFuel(airplane, tstep)

designMission.segments["climb"].initialize = _designMissionInitializeClimb
designMission.segments["climb"].completed = _designMissionCompletedClimb
designMission.segments["climb"].update = _designMissionUpdateClimb

# CRUISE

def _designMissionInitializeCruise(airplane, t, t0):
    airplane.flightPathAngle = 0 # level flight
    airplane.pitch = 0 # angle of attack to maintain
    airplane.speed = MaximumLiftOverDragVelocity(airplane) # speed to maintain
    # TODO: don't forget to make thrust what it should be to maintain this velocity
    airplane.throttle = 0.7

def _designMissionCompletedCruise(airplane, t, t0):
    return convert(300, "nmi", "m") <= airplane.position

def _designMissionUpdateCruise(airplane, t, tstep):
    airplane.position += airplane.speed * tstep
    UpdateFuel(airplane, tstep)

designMission.segments["cruise"].initialize = _designMissionInitializeCruise
designMission.segments["cruise"].completed = _designMissionCompletedCruise
designMission.segments["cruise"].update = _designMissionUpdateCruise

# DESCENT

def _designMissionInitializeDescent(airplane, t, t0):
    airplane.throttle = 0.3
    airplane.speed = convert(170, "kts", "m/s") # TODO: fix in same vein as with cruise velocity

def _designMissionCompletedDescent(airplane, t, t0):
    return airplane.altitude <= convert(100, "ft", "m")

def _designMissionUpdateDescent(airplane, t, tstep):
    _designMissionUpdateClimb(airplane, t, tstep) # DEBUG: does this work?

designMission.segments["descent"].initialize = _designMissionInitializeDescent
designMission.segments["descent"].completed = _designMissionCompletedDescent
designMission.segments["descent"].update = _designMissionUpdateDescent

# ABORT CLIMB

def _designMissionInitializeAbortClimb(airplane, t, t0):
    airplane.throttle = 1
    airplane.speed = convert(75, "kts", "m/s")
    # airplane.altitude = 0 # set for condition in descent
    # TODO: figure out why still descending

def _designMissionCompletedAbortClimb(airplane, t, t0):
    return loiterAltitude <= airplane.altitude

def _designMissionUpdateAbortClimb(airplane, t, tstep):
    _designMissionUpdateClimb(airplane, t, tstep) # DEBUG: does this work?

designMission.segments["abortClimb"].initialize = _designMissionInitializeAbortClimb
designMission.segments["abortClimb"].completed = _designMissionCompletedAbortClimb
designMission.segments["abortClimb"].update = _designMissionUpdateAbortClimb

# LOITER

def _designMissionInitializeLoiter(airplane, t, t0):
    # TODO: initialize properly
    airplane.throttle = 0.6
    airplane.flightPathAngle = 0
    airplane.pitch = 0
    airplane.speed = MaximumLiftOverDragVelocity(airplane) # speed to maintain

def _designMissionCompletedLoiter(airplane, t, t0):
    return loiterTime <= t - t0

def _designMissionUpdateLoiter(airplane, t, tstep):
    _designMissionUpdateCruise(airplane, t, tstep) # DEBUG: does this work?

designMission.segments["loiter"].initialize = _designMissionInitializeLoiter
designMission.segments["loiter"].completed = _designMissionCompletedLoiter
designMission.segments["loiter"].update = _designMissionUpdateLoiter

# ABORT DESCENT

def _designMissionInitializeAbortDescent(airplane, t, t0):
    airplane.throttle = 0.3
    airplane.speed = convert(170, "kts", "m/s") # TODO: fix in same vein as with cruise velocity

def _designMissionCompletedAbortDescent(airplane, t, t0):
    return airplane.altitude <= 0

def _designMissionUpdateAbortDescent(airplane, t, tstep):
    _designMissionUpdateClimb(airplane, t, tstep) # DEBUG: does this work?

designMission.segments["abortDescent"].initialize = _designMissionInitializeAbortDescent
designMission.segments["abortDescent"].completed = _designMissionCompletedAbortDescent
designMission.segments["abortDescent"].update = _designMissionUpdateAbortDescent

# LANDING

def _designMissionInitializeLanding(airplane, t, t0):
    airplane.pitch = 0
    airplane.flightPathAngle = 0
    airplane.altitude = 0
    airplane.throttle = 0

def _designMissionCompletedLanding(airplane, t, t0):
    return airplane.speed <= 0.1

def _designMissionUpdateLanding(airplane, t, tstep):
    # # see Raymer-v6 section 17.8.1
    # acceleration = accelerationOnGroundLanding(Airplane) # find acceleration from thrust, drag and ground friction
    # airplane.speed += acceleration * tstep # update speed with acceleration
    # airplane.position += airplane.speed * tstep # update position with speed
    # updateFuel(Airplane) # update the fuel
    _designMissionUpdateTakeoff(airplane, t, tstep) # DEBUG: does this work?

designMission.segments["landing"].initialize = _designMissionInitializeLanding
designMission.segments["landing"].completed = _designMissionCompletedLanding
designMission.segments["landing"].update = _designMissionUpdateLanding

# SHUTDOWN

def _designMissionInitializeShutdown(airplane, t, t0):
    airplane.throttle = 0.1

def _designMissionCompletedShutdown(airplane, t, t0):
    return convert(10, "min", "s") <= t - t0

def _designMissionUpdateShutdown(airplane, t, tstep):
    _designMissionUpdateStartup(airplane, t, tstep) # DEBUG: does this work?

designMission.segments["shutdown"].initialize = _designMissionInitializeShutdown
designMission.segments["shutdown"].completed = _designMissionCompletedShutdown
designMission.segments["shutdown"].update = _designMissionUpdateShutdown