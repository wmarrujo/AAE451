import sys
sys.path.insert(0, sys.path[0] + "/../")
from convert import convert # unit conversions
from stdatmo import * # standard atmospheric conditions
from scipy import * # math
from matplotlib.pyplot import * # plotting

from parameters import *
from constants import *
from equations import *

################################################################################
# AIRPLANE DEFINITION
################################################################################

airplane = Airplane()

################################################################################
# EVALUATION
################################################################################

# TODO: probably add this to an instance method as Mission.simulate(tstep)
t0 = 0
t = t0
tstep = 1 # s
for segment in designMission.segments:
    segment.initialize(airplane, t, t0)
    while not segment.completed(airplane, t, t0):
        segment.update(airplane, t, tstep)
        t0 = t
        t = t + tstep