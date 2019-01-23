# AAE 451 Senior Design Project Code
Code for the AAE 451 Senior Design Project

## Conventions

- comment. please.
- use long descriptive names for functions and variables
- for functions and variables that are not to be used outside their module, prefix with an underscore
- add description (the three double quotes) for any function that is not obvious
- state assumptions in comments for all equation functions

## Unit Conversions

examples:
```python
>>> from convert import convert
>>> convert(101325, "Pa", "psi")
14.695948732596014
>>> convert(180, "deg", "rad")
3.141592653589793
```

the unit strings are of a specific form:
- they must have only 0 1 or 2 parts separated by a division
- each term must be separated by an asterisk
- powers go directly after variables that need
- only positive powers, negative powers should be in the denominator

examples:
```python
"kg"
"m/s"
"kg*m/s^2"
"kg*m^2/s^3"
"1*m*kg^0.5*1*m*m^15*s/mol*K^3*A*cd*rad^2"
```