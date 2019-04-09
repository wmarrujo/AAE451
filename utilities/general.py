from functools import reduce
import copy
import numpy
import pickle
from hashlib import sha256

product = lambda L: reduce((lambda x, y: x * y), L)

def first(iterable, condition = lambda x: True):
    """
    Returns the first item in the `iterable` that
    satisfies the `condition`.
    
    If the condition is not given, returns the first item of
    the iterable.
    
    Raises `StopIteration` if no item satysfing the condition is found.
    
    >>> first( (1,2,3), condition=lambda x: x % 2 == 0)
    2
    >>> first(range(3, 100))
    3
    >>> first( () )
    Traceback (most recent call last):
    ...
    StopIteration
    """

    return next(x for x in iterable if condition(x))

def transpose(matrix):
    """
    transposes a 2-dimensional list
    """
    
    return [[matrix[r][c] for r in range(len(matrix))] for c in range(len(matrix[0]))]

class memoize:
    def __init__(self, f):
        self.f = f # function
        self.memo = {} # {input:output}
    def __call__(self, *args):
        inputHash = compareValue(*args)
        if not args in self.memo:
             value = self.f(*args)
             self.memo[inputHash] = value
             return value # so it doesn't have to do another lookup
        return self.memo[inputHash]

def compareValue(*objects):
    """
    provides a method which returns a comparable value (as a string) for any object
    defined solely by the values it contains (not its position in memory)
    """
    
    def hash(obj):
        return sha256(str(obj).encode("utf-8")).hexdigest()
    
    def _compareValue(obj):
        if "parameters" in str(type(obj)): # if it's an object (that's defined in parameters), make it recursive
            return hash(_compareValue(obj.__dict__)) # return a dictionary of comparable values
        elif type(obj) == list:
            return hash([_compareValue(item) for item in obj])
        elif type(obj) == dict:
            return hash({k:_compareValue(v) for (k, v) in obj.items()})
        elif type(obj) == numpy.float64: # numpy doesn't have __hash__ defined
            return _compareValue(obj.__repr__())
        else:
            return hash(obj)
    
    hashes = [_compareValue(obj) for obj in objects]
    return hash(hashes)

def saveObject(object, filePath):
    file = open(filePath, "wb")
    pickle.dump(object, file)
    file.close()

def loadObject(filePath):
    file = open(filePath, "rb")
    obj = pickle.load(file)
    file.close()
    return obj

def maybeReadAsNumber(string):
    try:
        return int(string)
    except Exception as e:
        try:
            return float(string)
        except Exception as e:
            return string