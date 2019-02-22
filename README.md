# AAE 451 Senior Design Project Code
Code for the AAE 451 Senior Design Project

## Sizing Organization

### Parameters

The source of the data for the equations in `equations.py`. These objects are written in the sizing code to correspond to specific missions or airplanes respectively.

### Equations

The `equations.py` file contains the equations used by the sizing code to calculate the airplane parameters.

### Sizing

In the sizing files, we define the airplane and mission, then run the equations 

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