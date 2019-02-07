from convert import convert

g = 9.80665 # m/s²
gasWeight = convert(263, "lb", "N")
gasMass = gasWeight / g # kg
gasEnergyDensity = 44e6 # J/kg
ηm = 0.35 # 
gasEnergy = ηm * gasMass * gasEnergyDensity # J
print(gasEnergy)

batteryEnergyDensity = convert(265, "Wh/kg", "J/kg")
batteryMass = gasEnergy / batteryEnergyDensity
batteryWeight = batteryMass * g

print("battery weight: {0:.0f} lb".format(convert(batteryWeight, "N", "lb")))