from scipy import *

################################################################################
# CONSTANTS
################################################################################

# EARTH VALUES
R = 287.058 # J/kg*K s# ideal gas constant for earth air
r = 6356766 # m # radius of the earth
g = 9.80665 # m/s² # gravitational acceleration at sea level
γ = 1.4 #  # air's ratio of specific heats

# ATMOSPHERE VALUES

_baseHeights = [0, 11000, 25000, 47000, 53000, 79000, 90000, 105000] # (geopotential) heights for the beginning of each layer, in m
_baseTemperatures = [288.16, 216.66, 216.66, 282.66, 282.66, 165.66, 165.66, 225.66] # temperature for the beginning of each layer, in K
_tempGradients = [-0.0065, 0, 0.003, 0, -0.0045, 0, 0.004, NaN] # temperature gradients for each layer, in K/m (last one represents no information above that height)
_basePressures = [101325.0, 22634.008746132295, 2489.1856086672196, 120.49268001877302, 58.347831704016428, 1.0101781258352585, 0.10452732009352216, nan] # in Pa # precalculated
_baseDensities = [1.225, 0.3639451299338376, 0.040025034448687088, 0.0014850787413445172, 0.00071914015402165508, 2.124386216253755e-05, 2.1981905205581133e-06, nan] # in kg/m^3 # precalculated

################################################################################
# EXPORTS
################################################################################

def _layerIndexForheight(h): # get a reference to the place in the lists where the base information is
    return _baseHeights.index(next(height for height in reversed(_baseHeights) if height <= h))

def _geopotentialAltitudeForHeight(hg):
    return (r * hg) / (r + hg)

def _temperatureAtHeight(h):
    i = _layerIndexForheight(h)
    return _baseTemperatures[i] + _tempGradients[i] * (h - _baseHeights[i])

def _isothermalLayerPressureAtHeight(h, basePressure, baseHeight, layerTemperature):
    return basePressure * exp(-(g * (h - baseHeight) / (R * layerTemperature)))

def _isothermalLayerDensityAtHeight(h, baseDensity, basePressure, pressureAtHeight):
    return baseDensity * (pressureAtHeight / basePressure)

def _gradientLayerPressureAtHeight(h, basePressure, temperatureAtHeight, baseTemperature, layerTemperatureGradient):
    return basePressure * (temperatureAtHeight / baseTemperature)**(-(g) / (R * layerTemperatureGradient))

def _gradientLayerDensityAtHeight(h, baseDensity, temperatureAtHeight, baseTemperature, layerTemperatureGradient):
    return baseDensity * (temperatureAtHeight / baseTemperature)**-(g/(R * layerTemperatureGradient) + 1)

def _baseInformation(h):
    i = _layerIndexForheight(h)
    return _baseHeights[i], _baseTemperatures[i], _tempGradients[i], _basePressures[i], _baseDensities[i]

def _informationAtHeight(hg):
    """Takes a Geometric Altitude and Returns the Geometric Altitude, Geopotential
     Altitude, Temperature, Pressure and Density at that altitude in that order.
     Defined from 0m to 105000m"""
    
    if hg >= 105000 or hg < 0: # if height out of range
        raise Exception("Atmosphere values unknown at altitudes above 105000m. This altitude: {0}m.".format(hg))
    
    h = _geopotentialAltitudeForHeight(hg)
    t = _temperatureAtHeight(h)

    baseHeight, baseTemperature, layerGradient, basePressure, baseDensity = _baseInformation(h)
    
    if (layerGradient == 0): # isothermal layer
        p = _isothermalLayerPressureAtHeight(h, basePressure, baseHeight, baseTemperature)
        d = _isothermalLayerDensityAtHeight(h, baseDensity, basePressure, p)
    else: # gradient layer
        p = _gradientLayerPressureAtHeight(h, basePressure, t, baseTemperature, layerGradient)
        d = _gradientLayerDensityAtHeight(h, baseDensity, t, baseTemperature, layerGradient)
    
    return hg, h, t, p, d

################################################################################
# REFERENCE FUNCTIONS
################################################################################

def temperatureAtAltitude(altitude):
    return _informationAtHeight(altitude)[2]

def pressureAtAltitude(altitude):
    return _informationAtHeight(altitude)[3]

def densityAtAltitude(altitude):
    return _informationAtHeight(altitude)[4]

def machAtAltitude(altitude):
    return sqrt(γ * R * temperatureAtAltitude(altitude))

def dynamicViscosityAtAltitude(altitude):
    temperature = temperatureAtAltitude(altitude)
    referenceDynamicViscosity = 1.729e-5 # kg/m*s
    referenceTemperature = 273.15 # K
    sutherlandTemperature = 110.4 # K
    return referenceDynamicViscosity * (temperature / referenceTemperature)**(3/2) * (referenceTemperature + sutherlandTemperature) / (temperature + sutherlandTemperature)

def kinematicViscosityAtAltitude(altitude):
    return dynamicViscosityAtAltitude(altitude) / densityAtAltitude(altitude)

################################################################################
# ATMOSPHERE OBJECT
################################################################################

class Air:
    altitude = 0 # m
    
    def __init__(self, altitude):
        self.altitude = altitude
    
    @property
    def temperature(self):
        return temperatureAtAltitude(altitude)
    
    @property
    def pressure(self):
        return pressureAtAltitude(altitude)
    
    @property
    def density(self):
        return densityAtAltitude(altitude)
    
    @property
    def mach(self):
        return sqrt(γ * R * self.temperature)