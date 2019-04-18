# PATHS

import sys
import os
hereDirectory = os.path.dirname(os.path.abspath(__file__))
rootDirectory = hereDirectory
sys.path.append(rootDirectory)

# LOCAL DEPENDENCIES

from utilities import *

from constants import *
from parameters import *
from missions import *
from equations import *
from sizing import *

# EXTERNAL DEPENDENCIES

from matplotlib.pyplot import *

################################################################################
# DEFINE AIRPLANE
################################################################################

W0 = convert(2711, "lb", "N")
Wf = convert(317, "lb", "N")
WS = convert(17.06, "lb/ft^2", "N/m^2")
PW = convert(0.072, "hp/lb", "W/N")

DPS = {"initial gross weight": W0, "initial fuel weight": Wf, "wing loading": WS, "power to weight ratio": PW}
PPs = getPerformanceParameters("tecnam", DPS, designMission)

ID = airplaneDefinitionID("tecnam", DPS)
airplane = loadFinalAirplane(ID)
simulation = loadSimulation(ID)
engine = airplane.engines[0]

################################################################################
# PRODUCTION COST
################################################################################

# Production Cost for 500, 1000, and 2000 Planned Aircraft
#
# plannedAircraft = 500
# production500 = ProductionCost(airplane,engine, plannedAircraft)
#
# plannedAircraft = 1000
# production1000 = ProductionCost(airplane, engine, plannedAircraft)
#
# plannedAircraft = 2000
# production2000 = ProductionCost(airplane, engine, plannedAircraft)

aircraftProduced = linspace(1, 1000)

# Production Cost For 500 Planned Aircraft

plannedAircraft = 500
fixedCost = FixedCost(airplane, plannedAircraft)
print("\nFor {:0.0f} planned aircraft:".format(plannedAircraft))
print("Fixed Cost = {:0.2f} USD".format(fixedCost))
variableCost = VariableCost(airplane, engine, plannedAircraft)
print("Variable Cost = {:0.2f} USD/aircraft".format(variableCost))

productionCost = (fixedCost / 500) + variableCost # cost per unit
print("Production Cost Per Aircraft = {:0.2f} USD/aircraft\n".format(productionCost))

productionList500 = [fixedCost, variableCost]

        # Breakeven Plot

salesPrice = [300000, 400000, 500000] # [2019 USD]

totalRevenueA = [salesPrice[0] * a for a in aircraftProduced]
totalRevenueB = [salesPrice[1] * a for a in aircraftProduced]
totalRevenueC = [salesPrice[2] * a for a in aircraftProduced]
totalProductionCost = [productionList500[0] + (productionList500[1] * a) for a in aircraftProduced]

figure()
plot(aircraftProduced, totalProductionCost, label = "Recurring and Non-Recurring Cost")
plot(aircraftProduced, totalRevenueA, label = "Low Sales Price")
plot(aircraftProduced, totalRevenueB, label = "Moderate Sales Price")
plot(aircraftProduced, totalRevenueC, label = "High Sales Price")
title("Breakeven Plot for {:0.0f} Planned Aircraft".format(plannedAircraft))
xlabel("Number of Aircraft Produced")
ylabel("Total Production Cost and Revenue [2019 USD]")
legend()

# Production Cost For 1000 Planned Aircraft

plannedAircraft = 1000
fixedCost = FixedCost(airplane, plannedAircraft)
print("\nFor {:0.0f} planned aircraft:".format(plannedAircraft))
print("Fixed Cost = {:0.2f} USD".format(fixedCost))
variableCost = VariableCost(airplane, engine, plannedAircraft)
print("Variable Cost = {:0.2f} USD/aircraft".format(variableCost))

productionCost = (fixedCost / 1000) + variableCost # cost per unit
#totalProductionCost500plot = [fixedCost + (variableCost * a) for a in aircraftProduced]
print("Production Cost Per Aircraft = {:0.2f} USD/aircraft\n".format(productionCost))

productionList1000 = [fixedCost, variableCost, productionCost]

# Production Cost For 2000 Planned Aircraft

plannedAircraft = 2000
fixedCost = FixedCost(airplane, plannedAircraft)
print("\nFor {:0.0f} planned aircraft:".format(plannedAircraft))
print("Fixed Cost = {:0.2f} USD".format(fixedCost))
variableCost = VariableCost(airplane, engine, plannedAircraft)
print("Variable Cost = {:0.2f} USD/aircraft".format(variableCost))

productionCost = (fixedCost / 2000) + variableCost # cost per unit
#totalProductionCost = [fixedCost + (variableCost * a) for a in aircraftProduced]
print("Production Cost Per Aircraft = {:0.2f} USD/aircraft\n".format(productionCost))

productionList2000 = [fixedCost, variableCost, productionCost]

# Define Breakeven Plot Function

# aircraftProduced = []
#
# def BreakevenPlot(productionList, aircraftProduced, plannedAircraft):

#     salesPrice = [300000, 400000, 500000] # [2019 USD]
#
#     totalRevenueA = [salesPrice[0] * a for a in aircraftProduced]
#     totalRevenueB = [salesPrice[1] * a for a in aircraftProduced]
#     totalRevenueC = [salesPrice[2] * a for a in aircraftProduced]
#     totalProductionCost = [productionList500[0] + (productionList[1] * a) for a in aircraftProduced]
#
#     figure()
#     plot(aircraftProduced, totalProductionCost, label = "Recurring and Non-Recurring Cost")
#     plot(aircraftProduced, totalRevenueA, label = "Low Sales Price")
#     plot(aircraftProduced, totalRevenueB, label = "Moderate Sales Price")
#     plot(aircraftProduced, totalRevenueC, label = "High Sales Price")
#     title("Breakeven Plot for {:0.0f} Planned Aircraft".format(plannedAircraft))
#     xlabel("Number of Aircraft Produced")
#     ylabel("Total Production Cost and Revenue [2019 USD]")
#     legend()
# #
#     return

# # Create Breakeven Plots
aircraftProduced = linspace(1, 1000)

# BreakevenPlot(productionList500, aircraftProduced, 500)
# BreakevenPlot(production1000, aircraftProduced, 1000)
# BreakevenPlot(production2000, aircraftProduced, 2000)

#
# priceA = 300000 # [2019 USD]
# priceB = 400000 # [2019 USD]
# priceC = 500000 # [2019 USD]
#
# totalRevenueA = [priceA * a for a in aircraftProduced]
# totalRevenueB = [priceB * a for a in aircraftProduced]
# totalRevenueC = [priceC * a for a in aircraftProduced]
#
# # Plots
#
# figure()
# plot(aircraftProduced, totalProductionCost500plot, label = "Recurring and Non-Recurring Cost")
# plot(aircraftProduced, totalRevenueA, label = "Low Sales Price")
# plot(aircraftProduced, totalRevenueB, label = "Moderate Sales Price")
# plot(aircraftProduced, totalRevenueC, label = "High Sales Price")
# title("Breakeven Plot for 500 Planned Aircraft")
# xlabel("Number of Aircraft Produced")
# ylabel("Total Production Cost and Revenue [2019 USD]")
# legend()


# Operating Cost

purchasePrice = 350000 # [2019 USD] # We set this based on breakevens above

totalAnnualOperatingCost = TotalAnnualCost(airplane, simulation, purchasePrice)
operatingCostPerHour = CostPerFlightHour(airplane, simulation, purchasePrice)
print("Total Annual Operating Cost {:0.2f} USD".format(totalAnnualOperatingCost))
print("Operating Cost Per Hour {:0.2f} USD".format(operatingCostPerHour))
