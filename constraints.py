from convert import convert
from matplotlib.pyplot import *
from scipy import *
from stdatmo import *

################################################################################
# CONSTANTS
################################################################################

g = 9.80665 # m/s²
β = 0.9 #  # weightFraction # FIXME: guessed
α = 0.8 #  # lapse rate # FIXME: guessed, raymer
V = convert(180, "kts", "m/s") # speed # FIXME: cruise speed
ηp = 0.9 # propeller efficiency # FIXME: guessed
q = 0.5*densityAtAltitude(0)*V**2 # dynamic pressure # FIXME: guessed
CD0 = 0.0218 #  # zero-lift drag # FIXME: raymer?
AR = 10 #  # aspect ratio # FIXME: guessed
e = 0.8 #  # oswald efficiency factor # FIXME: guessed
n = 1 #  # load factor # FIXME: guessed
dhdt = convert(100, "ft/min", "m/s") # top of climb rate
dVdt = 0 # m/s² # top of climb acceleration # TODO: figure out what this actually is
CLTO = 1.5 #  # takeoff lift coefficient # FIXME: guessed
CLLA = 1.85 #  # landing lift coefficient # FIXME: guessed
TOP = 200 # FIXME: guessed from raymer table 5.4 for 2000 ft takeoff distance
σ = 1 #  # density ratio of runway (sea level - sea level)
sland = convert(2000, "ft", "m") # landing distance 
glr = 5 #  # landing glide ratio # FIXME: guessed
ho = convert(50, "ft", "m") # height of obstacle
brf = convert(80, "ft^3/lb", "m^3/N") # braking factor on dry runway # FIXME: guessed raymer/slides

################################################################################
# CONSTRAINTS
################################################################################

# TAKEOFF

def takeoff(wingLoading):
    return β**2 * wingLoading / (α * TOP * σ * CLTO)

# CLIMB

def climb(wingLoading):
    return β/α * V/ηp * (q/β * (CD0/wingLoading + 1/(pi*AR*e) * (n*β/q)**2 * wingLoading) + 1/V * dhdt + 1/g * dVdt)

# CRUISE

def cruise(wingLoading):
    pass

# LANDING

sa = glr * ho
landing = σ * CLLA / (β * brf) * (sland - sa)

################################################################################
# PLOTS
################################################################################

wingLoadings = [convert(x, "lb/ft^2", "N/m^2") for x in range(10, 70)]
takeoffs = [takeoff(w) for w in wingLoadings]
climbs = [climb(w) for w in wingLoadings]

zeros = [0 for w in wingLoadings]
top = max(takeoffs + climbs) #convert(0.18, "hp/lb", "W/N")
right = wingLoadings[-1]

figure(1)
plot(wingLoadings, takeoffs, "g-", label="takeoff")
fill_between(wingLoadings, 0, takeoffs, color="g", alpha=0.3)
plot(wingLoadings, climbs, "b-", label="climb")
fill_between(wingLoadings, 0, climbs, color="b", alpha=0.3)
plot([landing, landing], [0, top], "r-", label="landing")
fill([landing, landing, right, right], [0, top, top, 0], color="r", alpha=0.3)
title("Constraints")
xlabel("Wing Loading [N/m²]")
ylabel("Power Loading [W/N]")
legend()

show()
