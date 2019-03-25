from functools import reduce

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
    transposes a 2 dimensional list
    """
    
    return [[matrix[r][c] for r in range(len(matrix))] for c in range(len(matrix[0]))]