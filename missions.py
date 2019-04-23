# LOCAL DEPENDENCIES

from utilities import *

from constants import *
from parameters import *
from equations import *

################################################################################
# DESIGN MISSION
################################################################################

designMission = Mission()
designMission.passengerFactor = 1
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
    airplane.altitude = 0
    airplane.speed = 0
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
designMission.segments["takeoff"].stepSizeFraction = 1/10

# CLIMB

def _designMissionInitializeClimb(airplane, t, t0):
    airplane.throttle = 1
    airplane.speed = VelocityForMaximumExcessPower(airplane)

def _designMissionCompletedClimb(airplane, t, t0):
    return cruiseAltitude <= airplane.altitude

designMission.segments["climb"].initialize = _designMissionInitializeClimb
designMission.segments["climb"].completed = _designMissionCompletedClimb
designMission.segments["climb"].update = UpdateClimb
designMission.segments["climb"].stepSizeFraction = 1/3

# CRUISE

def _designMissionInitializeCruise(airplane, t, t0):
    airplane.flightPathAngle = 0 # level flight
    airplane.pitch = 0 # angle of attack to maintain
    airplane.throttle = 0.7

def _designMissionCompletedCruise(airplane, t, t0):
    return minimumRange <= airplane.position

def updateCruiseWithCDBuildup(airplane, t, t0):
    UpdateCruise(airplane, t, t0)

designMission.segments["cruise"].initialize = _designMissionInitializeCruise
designMission.segments["cruise"].completed = _designMissionCompletedCruise
# designMission.segments["cruise"].update = UpdateCruise
designMission.segments["cruise"].update = updateCruiseWithCDBuildup

# DESCENT

def _designMissionInitializeDescent(airplane, t, t0):
    airplane.throttle = 0

def _designMissionCompletedDescent(airplane, t, t0):
    return airplane.altitude <= convert(100, "ft", "m")

designMission.segments["descent"].initialize = _designMissionInitializeDescent
designMission.segments["descent"].completed = _designMissionCompletedDescent
designMission.segments["descent"].update = UpdateDescent
designMission.segments["descent"].stepSizeFraction = 1/3

# ABORT CLIMB

def _designMissionInitializeAbortClimb(airplane, t, t0):
    airplane.throttle = 1
    airplane.speed = VelocityForMaximumExcessPower(airplane)

def _designMissionCompletedAbortClimb(airplane, t, t0):
    return loiterAltitude <= airplane.altitude

designMission.segments["abortClimb"].initialize = _designMissionInitializeAbortClimb
designMission.segments["abortClimb"].completed = _designMissionCompletedAbortClimb
designMission.segments["abortClimb"].update = UpdateClimb
designMission.segments["abortClimb"].stepSizeFraction = 1/3

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
designMission.segments["abortDescent"].stepSizeFraction = 1/3

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
designMission.segments["landing"].stepSizeFraction = 1/10

# SHUTDOWN

def _designMissionInitializeShutdown(airplane, t, t0):
    airplane.speed = 0
    airplane.throttle = 0.1

def _designMissionCompletedShutdown(airplane, t, t0):
    return convert(10, "min", "s") <= t - t0

designMission.segments["shutdown"].initialize = _designMissionInitializeShutdown
designMission.segments["shutdown"].completed = _designMissionCompletedShutdown
designMission.segments["shutdown"].update = UpdateWaiting

######################################################################################
# REFERENCE MISSION
######################################################################################

referenceMission = Mission()
referenceMission.passengerFactor = 0.5
referenceMission.pilots = 1

referenceMission.segments = Segments([
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

def _referenceMissionInitializeStartup(airplane, t, t0):
    airplane.altitude = 0
    airplane.speed = 0
    airplane.throttle = 0.3
    airplane.position = 0
    airplane.pitch = 0
    airplane.flightPathAngle = 0

def _referenceMissionCompletedStartup(airplane, t, t0):
    return convert(10, "min", "s") <= t - t0

referenceMission.segments["startup"].initialize = _referenceMissionInitializeStartup
referenceMission.segments["startup"].completed = _referenceMissionCompletedStartup
referenceMission.segments["startup"].update = UpdateWaiting

# TAKEOFF

def _referenceMissionInitializeTakeoff(airplane, t, t0):
    airplane.throttle = 1

def _referenceMissionCompletedTakeoff(airplane, t, t0):
    return TakeoffSpeed(airplane) <= airplane.speed

referenceMission.segments["takeoff"].initialize = _referenceMissionInitializeTakeoff
referenceMission.segments["takeoff"].completed = _referenceMissionCompletedTakeoff
referenceMission.segments["takeoff"].update = UpdateTakeoff
referenceMission.segments["takeoff"].stepSizeFraction = 1/10

# CLIMB

def _referenceMissionInitializeClimb(airplane, t, t0):
    airplane.throttle = 1
    airplane.speed = VelocityForMaximumExcessPower(airplane)

def _referenceMissionCompletedClimb(airplane, t, t0):
    return cruiseAltitude <= airplane.altitude

referenceMission.segments["climb"].initialize = _referenceMissionInitializeClimb
referenceMission.segments["climb"].completed = _referenceMissionCompletedClimb
referenceMission.segments["climb"].update = UpdateClimb
referenceMission.segments["climb"].stepSizeFraction = 1/3

# CRUISE

def _referenceMissionInitializeCruise(airplane, t, t0):
    airplane.flightPathAngle = 0 # level flight
    airplane.pitch = 0 # angle of attack to maintain
    airplane.throttle = 0.7

def _referenceMissionCompletedCruise(airplane, t, t0):
    return referenceRange <= airplane.position

referenceMission.segments["cruise"].initialize = _referenceMissionInitializeCruise
referenceMission.segments["cruise"].completed = _referenceMissionCompletedCruise
referenceMission.segments["cruise"].update = UpdateCruise

# DESCENT

def _referenceMissionInitializeDescent(airplane, t, t0):
    airplane.throttle = 0

def _referenceMissionCompletedDescent(airplane, t, t0):
    return airplane.altitude <= convert(100, "ft", "m")

referenceMission.segments["descent"].initialize = _referenceMissionInitializeDescent
referenceMission.segments["descent"].completed = _referenceMissionCompletedDescent
referenceMission.segments["descent"].update = UpdateDescent
referenceMission.segments["descent"].stepSizeFraction = 1/3

# ABORT CLIMB

def _referenceMissionInitializeAbortClimb(airplane, t, t0):
    airplane.throttle = 1
    airplane.speed = VelocityForMaximumExcessPower(airplane)

def _referenceMissionCompletedAbortClimb(airplane, t, t0):
    return loiterAltitude <= airplane.altitude

referenceMission.segments["abortClimb"].initialize = _referenceMissionInitializeAbortClimb
referenceMission.segments["abortClimb"].completed = _referenceMissionCompletedAbortClimb
referenceMission.segments["abortClimb"].update = UpdateClimb
referenceMission.segments["abortClimb"].stepSizeFraction = 1/3

# LOITER

def _referenceMissionInitializeLoiter(airplane, t, t0):
    # TODO: initialize properly
    airplane.throttle = 0.6
    airplane.flightPathAngle = 0
    airplane.pitch = 0
    airplane.speed = MaximumLiftOverDragVelocity(airplane) # speed to maintain

def _referenceMissionCompletedLoiter(airplane, t, t0):
    return loiterTime <= t - t0

referenceMission.segments["loiter"].initialize = _referenceMissionInitializeLoiter
referenceMission.segments["loiter"].completed = _referenceMissionCompletedLoiter
referenceMission.segments["loiter"].update = UpdateCruise

# ABORT DESCENT

def _referenceMissionInitializeAbortDescent(airplane, t, t0):
    airplane.throttle = 0.3
    airplane.speed = convert(170, "kts", "m/s") # TODO: fix in same vein as with cruise velocity

def _referenceMissionCompletedAbortDescent(airplane, t, t0):
    return airplane.altitude <= 0

referenceMission.segments["abortDescent"].initialize = _referenceMissionInitializeAbortDescent
referenceMission.segments["abortDescent"].completed = _referenceMissionCompletedAbortDescent
referenceMission.segments["abortDescent"].update = UpdateDescent
referenceMission.segments["abortDescent"].stepSizeFraction = 1/3

# LANDING

def _referenceMissionInitializeLanding(airplane, t, t0):
    airplane.pitch = 0
    airplane.flightPathAngle = 0
    airplane.altitude = 0
    airplane.throttle = 0

def _referenceMissionCompletedLanding(airplane, t, t0):
    return airplane.speed <= 0.1

referenceMission.segments["landing"].initialize = _referenceMissionInitializeLanding
referenceMission.segments["landing"].completed = _referenceMissionCompletedLanding
referenceMission.segments["landing"].update = UpdateLanding
referenceMission.segments["landing"].stepSizeFraction = 1/10

# SHUTDOWN

def _referenceMissionInitializeShutdown(airplane, t, t0):
    airplane.speed = 0
    airplane.throttle = 0.1

def _referenceMissionCompletedShutdown(airplane, t, t0):
    return convert(10, "min", "s") <= t - t0

referenceMission.segments["shutdown"].initialize = _referenceMissionInitializeShutdown
referenceMission.segments["shutdown"].completed = _referenceMissionCompletedShutdown
referenceMission.segments["shutdown"].update = UpdateWaiting

######################################################################################
# ABORTED TAKEOFF
######################################################################################
# Takeoff, abort the mission & immediately come back to land.

abortedMission = Mission()
abortedMission.passengerFactor = 1
abortedMission.pilots = 1

abortedMission.segments = Segments([
    Segment("startup"),
    Segment("takeoff"),
    Segment("climb"),
    Segment("cruise"),
    Segment("descent"),
    Segment("landing"),
    Segment("shutdown")
    ])

# STARTUP

def _abortedMissionInitializeStartup(airplane, t, t0):
    airplane.altitude = 0
    airplane.speed = 0
    airplane.throttle = 0.3
    airplane.position = 0
    airplane.pitch = 0
    airplane.flightPathAngle = 0

def _abortedMissionCompletedStartup(airplane, t, t0):
    return convert(10, "min", "s") <= t - t0

abortedMission.segments["startup"].initialize = _abortedMissionInitializeStartup
abortedMission.segments["startup"].completed = _abortedMissionCompletedStartup
abortedMission.segments["startup"].update = UpdateWaiting

# TAKEOFF

def _abortedMissionInitializeTakeoff(airplane, t, t0):
    airplane.throttle = 1

def _abortedMissionCompletedTakeoff(airplane, t, t0):
    return TakeoffSpeed(airplane) <= airplane.speed

abortedMission.segments["takeoff"].initialize = _abortedMissionInitializeTakeoff
abortedMission.segments["takeoff"].completed = _abortedMissionCompletedTakeoff
abortedMission.segments["takeoff"].update = UpdateTakeoff
abortedMission.segments["takeoff"].stepSizeFraction = 1/10

# CLIMB

def _abortedMissionInitializeClimb(airplane, t, t0):
    airplane.throttle = 1
    airplane.speed = VelocityForMaximumExcessPower(airplane)

def _abortedMissionCompletedClimb(airplane, t, t0):
    return convert(1000, "ft", "m") <= airplane.altitude

abortedMission.segments["climb"].initialize = _abortedMissionInitializeClimb
abortedMission.segments["climb"].completed = _abortedMissionCompletedClimb
abortedMission.segments["climb"].update = UpdateClimb
abortedMission.segments["climb"].stepSizeFraction = 1/5

# CRUISE

def _abortedMissionInitializeCruise(airplane, t, t0):
    airplane.flightPathAngle = 0 # level flight
    airplane.pitch = 0 # angle of attack to maintain
    airplane.throttle = 0.7

def _abortedMissionCompletedCruise(airplane, t, t0):
    return convert(3, "min", "s") <= t-t0 # don't fly the cruise, do 1 loop of the pattern for 3 min

abortedMission.segments["cruise"].initialize = _abortedMissionInitializeCruise
abortedMission.segments["cruise"].completed = _abortedMissionCompletedCruise
abortedMission.segments["cruise"].update = UpdateCruise

# DESCENT

def _abortedMissionInitializeDescent(airplane, t, t0):
    airplane.throttle = 0

def _abortedMissionCompletedDescent(airplane, t, t0):
    return airplane.altitude <= convert(5, "ft", "m")

abortedMission.segments["descent"].initialize = _abortedMissionInitializeDescent
abortedMission.segments["descent"].completed = _abortedMissionCompletedDescent
abortedMission.segments["descent"].update = UpdateDescent
abortedMission.segments["descent"].stepSizeFraction = 1/5

# LANDING

def _abortedMissionInitializeLanding(airplane, t, t0):
    airplane.pitch = 0
    airplane.flightPathAngle = 0
    airplane.altitude = 0
    airplane.throttle = 0

def _abortedMissionCompletedLanding(airplane, t, t0):
    return airplane.speed <= 0.1

abortedMission.segments["landing"].initialize = _abortedMissionInitializeLanding
abortedMission.segments["landing"].completed = _abortedMissionCompletedLanding
abortedMission.segments["landing"].update = UpdateLanding
abortedMission.segments["landing"].stepSizeFraction = 1/10

# SHUTDOWN

def _abortedMissionInitializeShutdown(airplane, t, t0):
    airplane.speed = 0
    airplane.throttle = 0.1

def _abortedMissionCompletedShutdown(airplane, t, t0):
    return convert(10, "min", "s") <= t - t0

abortedMission.segments["shutdown"].initialize = _abortedMissionInitializeShutdown
abortedMission.segments["shutdown"].completed = _abortedMissionCompletedShutdown
abortedMission.segments["shutdown"].update = UpdateWaiting
