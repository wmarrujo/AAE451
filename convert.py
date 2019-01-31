def convert(value, fromUnit, toUnit):
    """number -> string -> string
    NOTE: does not check if dimensions are the same
    """
    fromMultiplier = _parseUnit(fromUnit)
    toMultiplier = _parseUnit(toUnit)
    return value * fromMultiplier / toMultiplier

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
    "mm": 1e-3, # m
    "cm": 1e-2, # m
    "km": 1e3, # m
    "mi": 1609.34, # m
    "nmi": 1852, # m
    "g": 1e-3, # kg
    "min": 60, # s
    "hr": 60*60, # s
    "deg": 0.017453292519943295, # rad
    "lb": 4.4482216282509, # kg*m/s^2
    "in": 0.0254, # m
    "ft": 0.3048, # m
    "hp": 745.7, # kg*m^2/s^3
    "kts": 0.514444, # m/s
    "R": 5/9, # K
    "GBP": 1.3, # USD # Jan 2019
    "EUR": 1.14, # USD # Jan 2019
    "L": 1e-3, # m^3
    "gal": 0.00378541} # m^3

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
    "fps": "ft/s"}