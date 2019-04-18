def convert(value, fromUnit, toUnit):
    """number -> string -> string
    NOTE: does not check if dimensions are the same
    """
    
    # Deal with F & C offsets
    if fromUnit == "degF":
        value += 459.67
        fromUnit = "R"
    elif fromUnit == "degC":
        value += 273.15
        fromUnit = "K"

    
    if toUnit == "degF":
        offset = -459.67
        toUnit = "R"
    elif toUnit == "degC":
        offset = -273.15
        toUnit = "K"
    else:
        offset = 0
    
    fromMultiplier = _parseUnit(fromUnit)
    toMultiplier = _parseUnit(toUnit)
    
    return value * fromMultiplier / toMultiplier + offset

def _parseUnit(unitString):
    """string -> multiplier
    returns how many of the base SI units are equivalent to this unit
    """
    [num, den, *junk] = unitString.split("/") + ["1", "1"] # split string into numerator and denominator
    [num, den] = [x.split("*") for x in [num, den]] # split by term
    [num, den] = [[tuple(term.split("^")) for term in x] for x in [num, den]] # split unit & power
    [num, den] = [[(term[0], float(term[1]) if len(term) > 1 else 1) for term in x] for x in [num, den]] # convert power to number
    terms = num + list(map(lambda term: (term[0], -term[1]), den)) # join with negative exponents for denominator
    multiplier = 1
    for term in terms:
        multiplier *= _convertUnit(term[0])**term[1] # combine
    return multiplier

def _convertUnit(unit):
    """unit -> multiplier"""
    if unit in _derivedUnits:
        return _parseUnit(_derivedUnits[unit])
    elif unit in _scaledUnits:
        return _scaledUnits[unit]
    elif unit in _baseUnits:
        return 1
    else:
        raise Exception("unknown unit: {0}".format(unit))

_baseUnits = ["1", "m", "kg", "s", "K", "A", "mol", "cd", "rad", "USD"]

# NOTE: multipliers are 1 of these is how many of base SI unit of same dimension
_scaledUnits = { # {scaledUnit: multiplier}
    # length # m
    "ym": 1e-24,
    "zm": 1e-21,
    "am": 1e-18,
    "fm": 1e-15,
    "pm": 1e-12,
    "nm": 1e-9,
    "μm": 1e-6,
    "mm": 1e-3,
    "cm": 1e-2,
    "dm": 1e-1,
    "dam": 1e1,
    "hm": 1e2,
    "km": 1e3,
    "Mm": 1e6,
    "Gm": 1e9,
    "Tm": 1e12,
    "Pm": 1e15,
    "Em": 1e18,
    "Zm": 1e21,
    "Ym": 1e24,
    "Å": 100e-9,
    "in": 0.0254,
    "ft": 0.3048,
    "yd": 0.9144,
    "rd": 5.0292,
    "fur": 201.168,
    "mi": 1609.344,
    "nmi": 1852,
    "ly": 9460730472580800,
    "pc": 30856775814671900,
    "li": 0.201168,
    "ch": 20.1168,
    # mass # kg
    "mg": 1e-6,
    "cg": 1e-5,
    "dg": 1e-4,
    "g": 1e-3,
    "dag": 1e-2,
    "hg": 1e-1,
    "Mg": 1e3,
    "slug": 14.5939,
    # time # s
    "min": 60,
    "hr": 60*60,
    # Angle # rad
    "deg": 0.017453292519943295,
    "rev": 6.2831853072,
    # Temperature # K
    "R": 5/9,
    # Charge # s*A (C)
    "mAh": 3.6,
    "Ah": 3600,
    # Speed # m/s
    "kts": 0.514444,
    # Area # m^2
    "acre": 4046.86,
    # Volume # m^3
    "mL": 1e-6,
    "cL": 1e-5,
    "dL": 1e-4,
    "L": 1e-3,
    "hL": 1e-1,
    "kL": 1,
    "gal": 0.003785411784,
    "pt": 0.000473176473,
    "qt": 0.000946352946,
    "gi": 0.0001182941183,
    "bu": 0.03523907017,
    "pk": 0.008809767542,
    # Money # USD
    "GBP": 1.3, # Jan 2019
    "EUR": 1.14, # Jan 2019
    # Force # kg*m/s^2 (N)
    "yN": 1e-24,
    "zN": 1e-21,
    "aN": 1e-18,
    "fN": 1e-15,
    "pN": 1e-12,
    "nN": 1e-9,
    "μN": 1e-6,
    "mN": 1e-3,
    "cN": 1e-2,
    "dN": 1e-1,
    "daN": 1e1,
    "hN": 1e2,
    "kN": 1e3,
    "MN": 1e6,
    "GN": 1e9,
    "TN": 1e12,
    "PN": 1e15,
    "EN": 1e18,
    "ZN": 1e21,
    "YN": 1e24,
    "lb": 4.4482216282509,
    # Energy # kg*m^2/s^2 (J)
    "yJ": 1e-24,
    "zJ": 1e-21,
    "aJ": 1e-18,
    "fJ": 1e-15,
    "pJ": 1e-12,
    "nJ": 1e-9,
    "μJ": 1e-6,
    "mJ": 1e-3,
    "cJ": 1e-2,
    "dJ": 1e-1,
    "daJ": 1e1,
    "hJ": 1e2,
    "kJ": 1e3,
    "MJ": 1e6,
    "GJ": 1e9,
    "TJ": 1e12,
    "PJ": 1e15,
    "EJ": 1e18,
    "ZJ": 1e21,
    "YJ": 1e24,
    "eV": 1.60218e-19,
    "cal": 4.184,
    "kcal": 4184,
    "Wh": 3.6e3,
    "kWh": 3.6e6,
    "btu": 1055.06,
    # Power # kg*m^2/s^3 (W)
    "yW": 1e-24,
    "zW": 1e-21,
    "aW": 1e-18,
    "fW": 1e-15,
    "pW": 1e-12,
    "nW": 1e-9,
    "μW": 1e-6,
    "mW": 1e-3,
    "cW": 1e-2,
    "dW": 1e-1,
    "daW": 1e1,
    "hW": 1e2,
    "kW": 1e3,
    "MW": 1e6,
    "GW": 1e9,
    "TW": 1e12,
    "PW": 1e15,
    "EW": 1e18,
    "ZW": 1e21,
    "YW": 1e24,
    "hp": 745.7,
    }
    

# NOTE: baseUnitConstruction must be made of only units in _baseUnits or _scaledUnits
_derivedUnits = { # {derivedUnit: baseUnitConstruction}
    "N": "kg*m/s^2",
    "J": "kg*m^2/s^2",
    "W": "kg*m^2/s^3",
    "Hz": "1/s",
    "C": "s*A",
    "V": "kg*m^2/s^3*A",
    "F": "s^4*A^2/kg*m^2",
    "Ω": "kg*m^2/s^3*A^2",
    "S": "s^3*A^2/kg*m^2",
    "Wb": "kg*m^2/s^2*A",
    "T": "kg/s^2*A",
    "H": "kg*m^2/s^2*A^2",
    "lx": "cd/m^2",
    "Pa": "kg/s^2*m",
    "psi": "lb/in^2",
    "mph": "mi/hr",
    "fps": "ft/s",
    "degR": "R",
    "RPM": "rev/min",
    }
