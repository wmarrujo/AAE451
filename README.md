# AAE 451 Senior Design Project Code
Code for the AAE 451 Senior Design Project

## Sizing Organization

### Constants

This is where all of the universal constants will go. Stuff like gravitational acceleration `g` or energy density of avgas.

### Parameters

Contains the objects that organize the configuration data that we have. Instances of these objects are passed as the data in the equations.

- The `Mission` object contains all the information about a given sizing mission.
- The `Airplane` object contains all the information about a given airplane configuration.
- Other objects (such as powerplant or wing) are set up to fit into an instance variable in either the `Mission` or `Airplane` objects in order to be able to swap in and out different components

### Equations

Here are defined the equations that take the mission and aircraft parameters and calculate performance values.

### Missions

The missions file is where each mission is defined. Each mission has a segments list, where each segment has an initialize function, completion condition function, and an update function. The structure for these is defined in the parameters function.

### Sizing

This file defines how the aircraft sizing is done.

It has a function to close the aircraft weight by finding the guessed weight of the airplane that leads to the same prediction.s

## Simulations

This folder is where the simulation cache goes. It is not tracked by git so we can all test independently. To clear the cache, just delete the contents of the directory.

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

## Conventions

### Organizational

- All time-dependent data will stem from the information about the mission segments
- Equation names are fully written out names: `FuelWeight` vs. `Wf`
- Inside equation, all variables to be used in calculation are defined first via their respective functions (and commented if ambiguous)
- Inside equation, all Variable names to be used in calculation are with shortened names 'Wf' vs. `FuelWeight`
- Keep iteration from guesses in the sizing file, not in the equations, definitions, or parameters section

### Programming Practice

- Use camel case: `CoefficientOfThrust` vs. `coefficientofthrust`
- Don't use underscores: `CLmax` vs. `CL_max`
- Functions and Classes start with capital letter: `LandingDistance` vs. `landingDistance`
- Variables don't start with capital letter: `missionSegment` vs. `MissionSegment` (unless it only makes sense that way)
- for greek characters, write out full name: `gamma` for `γ`, and if capital version, capitalize: `Gamma` for `Γ`
- for derivative or fractional values, write the same, but ignore division sign: `dhdt` for `dh/dt` and `CLCD` for `CL/CD`