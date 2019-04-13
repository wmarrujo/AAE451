from utilities import *

from constants import *
from parameters import *

from equations import *
from sizing import *

import sys
import os
sys.path.append(os.path.join(sys.path[0], "configurations"))
from testcraft import airplane as testcraft

###
DPS = [convert(17.06, "lb/ft^2", "N/m^2"), convert(0.072, "hp/lb", "W/N")]

airplane = defineAirplane(DPS, testcraft)
engines = airplane.engines

################################################################################
# COST
################################################################################

aircraftProduced = linspace(1, 1000)
# plannedAircraft = [500,1000,2000]

# Total Production Cost for 500 Aircraft
################# write functions for these instead of copy paste

plannedAircraft = 500
developmentCost = FixedCost(airplane, plannedAircraft)
print("\nFixedCost500 = {:0.2f} USD".format(developmentCost))
productionCost = VariableCost(airplane, engines, plannedAircraft)
print("VariableCost500 = {:0.2f} USD/aircraft".format(productionCost))

productionCost500 = (developmentCost / 500) + productionCost # cost per unit
totalProductionCost500plot = [developmentCost + (productionCost * a) for a in aircraftProduced]
print("TotalProducationCost500 = {:0.2f} USD/aircraft\n".format(productionCost500))

# Total Production Cost for 1000 Aircraft

plannedAircraft = 1000
developmentCost = FixedCost(airplane, plannedAircraft)
print("\nFixedCost1000 = {:0.2f} USD".format(developmentCost))
productionCost = VariableCost(airplane, engines, plannedAircraft)
print("VariableCost1000 = {:0.2f} USD/aircraft".format(productionCost))

productionCost1000 = (developmentCost / 1000) + productionCost  # cost per unit
totalProductionCost1000plot = [developmentCost + (productionCost * a) for a in aircraftProduced]
print("TotalProductionCost1000 = {:0.2f} USD/aircraft\n".format(productionCost1000))

# Total Production Cost for 2000 Aircraft

plannedAircraft = 2000
developmentCost = FixedCost(airplane, plannedAircraft)
print("\nFixedCost2000 = {:0.2f} USD".format(developmentCost))
productionCost = VariableCost(airplane, engines, plannedAircraft)
print("VariableCost2000 = {:0.2f} USD/aircraft".format(productionCost))

productionCost2000 = (developmentCost / 2000) + productionCost # cost per unit
totalProductionCost2000plot = [developmentCost + (productionCost * a) for a in aircraftProduced]
print("TotalProductionCost2000 = {:0.2f} USD/aircraft\n".format(productionCost2000))

# Revenue Calculations
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
#
# purchasePrice = 450000 # [2019 USD] # We set this based on breakevens above
# IFRflight = True
#
# totalAnnualOperatingCost = TotalAnnualCost(airplane)
# operatingCostPerHour = CostPerFlightHour(airplane)
# print("totalAnnualOperatingCost {0.00} USD".format(totalAnnualOperatingCost))
# print("operatingCostPerHour {0.00} USD".format(operatingCostPerHour))
