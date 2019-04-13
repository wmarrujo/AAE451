# LOCAL DEPENDENCIES

from utilities import *

from constants import *
from parameters import *
from equations import *

################################################################################
# COST
################################################################################

# DAPCA model Raymer v6 18.4.2 (just development and production cost)
# still need maintenance cost, crew cost, insurance cost, and fuel/oil cost

def RDTE(Airplane):
    He = engineeringHours(Airplane)
    Ht = toolingHours(Airplane)
    Hm = manufacturingHours(Airplane)
    Hq = qualityControlHours(Airplane)

    Re = engineeringWrapRate
    Rt = toolingWrapRate
    Rq = qualityControlWrapRate
    Rm = maunufacturingWrapRate

    Cd = developmentSupportCost(Airplane)
    Cf = flightTestCost(Airplane)
    Cm = manufacturingMaterialsCost(Airplane)
    Cen = Airplane.engine.cost
    Ca = Airplane.avionicsCost
    Cp = passengerAdditionalCost(Airplane)

    Nen = Airplane.engine.cost
    iR = inflation2012to2019

    return He*Re*iR + Ht*Rt*iR + Hm*Rm*iR + Hq*Rq*iR + Cd + Cf + Cm + Cen*Nen + Ca + Cp
