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
# DEFINE AIRPLANES
################################################################################

WS = convert(20, "lb/ft^2", "N/m^2")
PW = convert(0.08, "hp/lb", "W/N")

DPS = {"wing loading": WS, "power to weight ratio": PW}

data = getAirplaneDesignData("Gopher", DPS, designMission)
PPs = getPerformanceParameters(data["initial airplane"], data["simulation"], data["final airplane"])

airplane = data["initial airplane"]
simulation = data["simulation"]
engine = airplane.engines[0]

dataR = getAirplaneDesignData("Gopher", DPS, referenceMission)
PPsR = getPerformanceParameters(data["initial airplane"], data["simulation"], data["final airplane"])

airplaneR = data["initial airplane"]
simulationR = data["simulation"]
engineR = airplane.engines[0]

################################################################################
# PRODUCTION COST
################################################################################

salesPrice = [750000, 650000, 550000] # [2019 USD]

# Production Cost For 500 Planned Aircraft

plannedAircraft = 500
fixedCost =FixedCost(airplane, plannedAircraft)
print("\nFor {:0.0f} planned aircraft:".format(plannedAircraft))
print("Fixed Cost = {:0.2f} USD".format(fixedCost))
variableCost = VariableCost(airplane, engine, plannedAircraft)
print("Variable Cost = {:0.2f} USD/aircraft".format(variableCost))

productionCost = (fixedCost / 500) + variableCost # cost per unit
print("Production Cost Per Aircraft = {:0.2f} USD/aircraft".format(productionCost))

    # Breakeven Aircraft

NbeA = fixedCost / (salesPrice[0] - variableCost)
NbeB = fixedCost / (salesPrice[1] - variableCost)
NbeC = fixedCost / (salesPrice[2] - variableCost)
print("Breakeven Aircraft at {:0.2f} USD is {:0.0f}".format(salesPrice[0], NbeA))
print("Breakeven Aircraft at {:0.2f} USD is {:0.0f}".format(salesPrice[1], NbeB))
print("Breakeven Aircraft at {:0.2f} USD is {:0.0f}\n".format(salesPrice[2], NbeC))

# Production Cost For 1000 Planned Aircraft

plannedAircraft = 1000
fixedCost = FixedCost(airplane, plannedAircraft)
print("\nFor {:0.0f} planned aircraft:".format(plannedAircraft))
print("Fixed Cost = {:0.2f} USD".format(fixedCost))
variableCost = VariableCost(airplane, engine, plannedAircraft)
print("Variable Cost = {:0.2f} USD/aircraft".format(variableCost))

productionCost = (fixedCost / 1000) + variableCost # cost per unit
#totalProductionCost500plot = [fixedCost + (variableCost * a) for a in aircraftProduced]
print("Production Cost Per Aircraft = {:0.2f} USD/aircraft".format(productionCost))

    # Breakeven Aircraft

NbeA = fixedCost / (salesPrice[0] - variableCost)
NbeB = fixedCost / (salesPrice[1] - variableCost)
NbeC = fixedCost / (salesPrice[2] - variableCost)
print("Breakeven Aircraft at {:0.2f} USD is {:0.0f}".format(salesPrice[0], NbeA))
print("Breakeven Aircraft at {:0.2f} USD is {:0.0f}".format(salesPrice[1], NbeB))
print("Breakeven Aircraft at {:0.2f} USD is {:0.0f}\n".format(salesPrice[2], NbeC))

# Production Cost For 2000 Planned Aircraft

plannedAircraft = 2000
fixedCost = FixedCost(airplane, plannedAircraft)
print("\nFor {:0.0f} planned aircraft:".format(plannedAircraft))
print("Fixed Cost = {:0.2f} USD".format(fixedCost))
variableCost = VariableCost(airplane, engine, plannedAircraft)
print("Variable Cost = {:0.2f} USD/aircraft".format(variableCost))

productionCost = (fixedCost / 2000) + variableCost # cost per unit
#totalProductionCost = [fixedCost + (variableCost * a) for a in aircraftProduced]
print("Production Cost Per Aircraft = {:0.2f} USD/aircraft".format(productionCost))

    # Breakeven Aircraft

NbeA = fixedCost / (salesPrice[0] - variableCost)
NbeB = fixedCost / (salesPrice[1] - variableCost)
NbeC = fixedCost / (salesPrice[2] - variableCost)
print("Breakeven Aircraft at {:0.2f} USD is {:0.0f}".format(salesPrice[0], NbeA))
print("Breakeven Aircraft at {:0.2f} USD is {:0.0f}".format(salesPrice[1], NbeB))
print("Breakeven Aircraft at {:0.2f} USD is {:0.0f}\n".format(salesPrice[2], NbeC))

# Operating Cost

purchasePrice = 400000 # [2019 USD] # We set this based on breakevens above

totalAnnualOperatingCost = TotalAnnualCost(airplaneR, simulationR, purchasePrice)
operatingCostPerHour = CostPerFlightHour(airplaneR, simulationR, purchasePrice)
print("Total Annual Operating Cost {:0.2f} USD".format(totalAnnualOperatingCost))
print("Operating Cost Per Hour {:0.2f} USD/hr".format(operatingCostPerHour))


###### An attempt at breakeven plots
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
# aircraftProduced = linspace(1, 1000)
