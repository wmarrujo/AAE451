import sys
sys.path.insert(0, sys.path[0] + "/../")
from convert import convert # unit conversions
from stdatmo import * # standard atmospheric conditions
from scipy import * # math
from matplotlib.pyplot import * # plotting
import copy

from convert import convert
from parameters import *
from constants import *
from equations import *

################################################################################
# COST
################################################################################

numberFlightTestAircraft = 4
compFraction = 0
Airplane.speed = 100
emptyWeight = 2500
retractableGear = True

aircraftProduced = linspace(1, 1000)

# Total Production Cost for 500 Aircraft

plannedAircraft = 500
developmentCost = fixedCost(airplane)
productionCost = variableCost(airplane)

productionCost500 = (developmentCost / 500) + productionCost # cost per unit
totalProductionCost500plot = developmentCost + (productionCost * aircraftProduced) for a in aircraftProduced
print("productionCost500 {0.00} USD".format(productionCost500))

# Total Production Cost for 1000 Aircraft

plannedAircraft = 1000
developmentCost = fixedCost(airplane)
productionCost = variableCost(airplane)

productionCost1000 = (developmentCost / 1000) + productionCost  # cost per unit
totalProductionCost1000plot = developmentCost + (productionCost * aircraftProduced) for a in aircraftProduced
print("productionCost1000 {0.00} USD".format(productionCost1000))

# Total Production Cost for 2000 Aircraft

plannedAircraft = 2000
developmentCost = fixedCost(airplane)
productionCost = variableCost(airplane)

productionCost2000 = (developmentCost / 2000) + productionCost # cost per unit
totalProductionCost2000plot = developmentCost + (productionCost * aircraftProduced) for a in aircraftProduced
print("productionCost2000 {0.00} USD".format(productionCost2000))

# Revenue Calculations

priceA = 300000 # [2019 USD]
priceB = 400000 # [2019 USD]
priceC = 500000 # [2019 USD]

totalRevenueA = priceA * aircraftProduced for a in aircraftProduced
totalRevenueB = priceB * aircraftProduced for a in aircraftProduced
totalRevenueC = priceC * aircraftProduced for a in aircraftProduced

# Plots

figure()
plot(aircraftProduced, totalProductionCost500plot, label = "Recurring and Non-Recurring Cost")
plot(aircraftProduced, totalRevenueA, label = "Low Sales Price")
plot(aircraftProduced, totalRevenueB, label = "Moderate Sales Price")
plot(aircraftProduced, totalRevenueC, label = "High Sales Price")
title("Breakeven Plot for 500 Planned Aircraft")
xlabel("Number of Aircraft Produced")
ylabel("Total Production Cost and Revenue [2019 USD]")
legend()

figure()
plot(aircraftProduced, totalProductionCost1000plot, label = "Recurring and Non-Recurring Cost")
plot(aircraftProduced, totalRevenueA, label = "Low Sales Price")
plot(aircraftProduced, totalRevenueB, label = "Moderate Sales Price")
plot(aircraftProduced, totalRevenueC, label = "High Sales Price")
title("Breakeven Plot for 1000 Planned Aircraft")
xlabel("Number of Aircraft Produced")
ylabel("Total Production Cost and Revenue [2019 USD]")
legend()

figure()
plot(aircraftProduced, totalProductionCost2000plot, label = "Recurring and Non-Recurring Cost")
plot(aircraftProduced, totalRevenueA, label = "Low Sales Price")
plot(aircraftProduced, totalRevenueB, label = "Moderate Sales Price")
plot(aircraftProduced, totalRevenueC, label = "High Sales Price")
title("Breakeven Plot for 2000 Planned Aircraft")
xlabel("Number of Aircraft Produced")
ylabel("Total Production Cost and Revenue [2019 USD]")
legend()

# Operating Cost

purchasePrice = 450000 # [2019 USD] # We set this based on breakevens above
IFRflight = True

totalAnnualOperatingCost = totalAnnualCost(airplane)
operatingCostPerHour = costPerFlightHour(airplane)
print("totalAnnualOperatingCost {0.00} USD".format(totalAnnualOperatingCost))
print("operatingCostPerHour {0.00} USD".format(operatingCostPerHour))
