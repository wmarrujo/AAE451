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

WS = convert(17.06, "lb/ft^2", "N/m^2")
PW = convert(0.072, "hp/lb", "W/N")
DPS = {"wing loading": WS, "power to weight ratio": PW}
airplane = defineAirplane("tecnam", DPS, designMission)
simulation = simulateMission(airplane, designMission)

################################################################################
# PRODUCTION COST
################################################################################

# Define Production Cost Function

def ProductionCost(airplane, plannedAircaft):
    fixedCost = FixedCost(airplane, plannedAircraft)
    variableCost = VariableCost(airplane, plannedAircraft)
    productionCost = (fixedCost/plannedAircraft) + variableCost
    
    print("\nFor {:0.0f} planned aircraft".format(plannedAircraft))
    print("Fixed Cost  = {:0.2f} USD".format(fixedCost))
    print("Variable Cost = {:0.2f} USD/aircraft".format(variableCost))
    print("Production Cost Per Unit = {:0.2f} USD/aircraft\n".format(productionCost))
    
    return [fixedCost, variableCost, productionCost]

# Production Cost for 500, 1000, and 2000 Planned Aircraft

production500 = ProductionCost(airplane, 500)
production1000 = ProductionCost(airplane, 1000)
production2000 = ProductionCost(airplane, 2000)

# plannedAircraft = 500
# fixedCost = FixedCost(airplane, plannedAircraft)
# print("\nFixedCost500 = {:0.2f} USD".format(fixedCost))
# variableCost = VariableCost(airplane, plannedAircraft)
# print("VariableCost500 = {:0.2f} USD/aircraft".format(variableCost))
#
# productionCost500 = (fixedCost / 500) + variableCost # cost per unit
# totalProductionCost500plot = [fixedCost + (variableCost * a) for a in aircraftProduced]
# print("ProducationCostPerAC500 = {:0.2f} USD/aircraft\n".format(productionCost500))

# Define Breakeven Plot Function

def BreakevenPlot(productionList, aircraftProduced, plannedAircraft):
    salesPrice = [300000, 400000, 500000] # [2019 USD]
    
    totalRevenueA = [salesPrice[0] * a for a in aircraftProduced]
    totalRevenueB = [salesPrice[1] * a for a in aircraftProduced]
    totalRevenueC = [salesPrice[2] * a for a in aircraftProduced]
    totalProductionCost = [productionList[0] + (productionList[1] * a) for a in aircraftProduced]

    figure()
    plot(aircraftProduced, totalProductionCost, label = "Recurring and Non-Recurring Cost")
    plot(aircraftProduced, totalRevenueA, label = "Low Sales Price")
    plot(aircraftProduced, totalRevenueB, label = "Moderate Sales Price")
    plot(aircraftProduced, totalRevenueC, label = "High Sales Price")
    title("Breakeven Plot for {:0.0f} Planned Aircraft".format(plannedAircraft))
    xlabel("Number of Aircraft Produced")
    ylabel("Total Production Cost and Revenue [2019 USD]")
    legend()
    
    return

# Create Breakeven Plots
aircraftProduced = linspace(1, 1000)

BreakevenPlot(production500, aircraftProduced, 500)
BreakevenPlot(production1000, aircraftProduced, 1000)
BreakevenPlot(production2000, aircraftProduced, 2000)

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
#
# figure()
# plot(aircraftProduced, totalProductionCost1000plot, label = "Recurring and Non-Recurring Cost")
# plot(aircraftProduced, totalRevenueA, label = "Low Sales Price")
# plot(aircraftProduced, totalRevenueB, label = "Moderate Sales Price")
# plot(aircraftProduced, totalRevenueC, label = "High Sales Price")
# title("Breakeven Plot for 1000 Planned Aircraft")
# xlabel("Number of Aircraft Produced")
# ylabel("Total Production Cost and Revenue [2019 USD]")
# legend()
#
# figure()
# plot(aircraftProduced, totalProductionCost2000plot, label = "Recurring and Non-Recurring Cost")
# plot(aircraftProduced, totalRevenueA, label = "Low Sales Price")
# plot(aircraftProduced, totalRevenueB, label = "Moderate Sales Price")
# plot(aircraftProduced, totalRevenueC, label = "High Sales Price")
# title("Breakeven Plot for 2000 Planned Aircraft")
# xlabel("Number of Aircraft Produced")
# ylabel("Total Production Cost and Revenue [2019 USD]")
# legend()

# Operating Cost

# purchasePrice = 350000 # [2019 USD] # We set this based on breakevens above
#
# totalAnnualOperatingCost = TotalAnnualCost(airplane, simulation)
# operatingCostPerHour = CostPerFlightHour(airplane)
# print("totalAnnualOperatingCost {:0.2f} USD".format(totalAnnualOperatingCost))
# print("operatingCostPerHour {:0.2f} USD".format(operatingCostPerHour))
