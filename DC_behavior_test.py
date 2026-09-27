import os
# Wipes the terminal screen completely clean before printing anything else
os.system('cls' if os.name == 'nt' else 'clear')

#----------------------------------------------------------------------------------
# BASIC COMPONENT'S FORMULAS
#----------------------------------------------------------------------------------

# Function for calculating the voltage of a resistor
def calculate_resistor_voltage(current, resistance):
    
    # Apply Ohm's Law
    resistor_voltage = current * resistance
    
    return resistor_voltage

# Function for calculating the current of a resistor
def calculate_resistor_current(voltage, resistance):
    
    # Apply Ohm's Law
    resistor_current = voltage/resistance
    
    return resistor_current

# Function for calculating the power of a resistor
def calculate_resistor_power(current, voltage):
    
    # Apply the power formula --> p = vi
    resistor_power = current * voltage
    
    return resistor_power

# Function for calculating the equivalent resistance of a parallel circuit
def calculate_eqr_parallel(resistances):
    equivalent_resistance = 0
    
    # Add the resistors in fractions
    for resistor in resistances:
        equivalent_resistance += 1/resistor
    
    # Elevate the obtained resistance to the power of -1
    equivalent_resistance **= -1
    
    return equivalent_resistance

# Calculate the equivalent resistance of a series circouit
def calculate_eqr_series(resistances):
    equivalent_resistance = 0
    
    # Add the resistor values directly in a for loop
    for resistor in resistances:
        equivalent_resistance += resistor
    
    return equivalent_resistance
