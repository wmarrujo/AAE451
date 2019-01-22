def convert(value, fromUnit, toUnit):
    """number -> string -> string
    ! does not check if dimensions are the same
    """
    fromMultiplier = _parseUnit(fromUnit)
    toMultiplier = _parseUnit(toUnit)
    return value * fromMultiplier / toMultiplier

# test string: "kg*m^2/s^2*mol*K"
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

_baseUnits = ["1", "m", "kg", "s", "K", "A", "mol", "cd", "rad"]

# NOTE: multipliers are to base SI unit of same dimension
_scaledUnits = { # {scaledUnit: multiplier}
    "mm": 1e-3,
    "km": 1e3,
    "mi": 1609.34,
    "g": 1e-3,
    "min": 60,
    "hr": 60*60,
    "deg": 0.017453292519943295,
    "lb": 4.4482216282509,
    "in": 0.0254,
    "ft": 0.3048}

# NOTE: baseUnitConstruction must be made of only units in _baseUnits or _scaledUnits
_derivedUnits = { # {derivedUnit: baseUnitConstruction}
    "N": "kg*m/s^2",
    "J": "kg*m^2/s^2",
    "W": "kg*m^2/s^3",
    "Pa": "kg/s^2*m",
    "psi": "lb/in^2"}