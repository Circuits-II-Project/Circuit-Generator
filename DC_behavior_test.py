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

#----------------------------------------------------------------------------------
# INDUCTORS FORMULAS
#----------------------------------------------------------------------------------

# Function for calculating the voltage of an inductor. We need multiple values:
# - inductance = Inductor value in Henries
# - previous_current = Initial current at starting time
# - current = Final current at end time
# - previous time = Initial time for the inductor
# - time = The final time after the inductor is disconnected from the battery
def calculate_inductor_voltage(inductance, previous_current, current, previous_time, time):
    
    # Substraction of the current difference: Final_current - Starting_current
    inductor_current = current - previous_current
    
    # Substraction of the time difference: Final_time - Starting_time
    inductor_time = time - previous_time
    
    # Formula for calculating the voltage of an inductor
    inductor_voltage = inductance *(inductor_current/inductor_time)
    
    return inductor_voltage


# Function for calculating the equivalent resistance of an inductor
# The equivalent inductance is calculated exactly like a resistor (parallel and series)
def calculate_eqi_parallel(inductances):
    equivalent_inductance = 0
        
    # Add the resistors in fractions
    for inductor in inductances:
        equivalent_inductance += 1/inductor
    
    # Eleveate the calculated value to the power of -1
    equivalent_inductance **= -1
    
    return equivalent_inductance

# Function for calculating the equivalent resistance of an inductor
def calculate_eqi_series(inductances):
    equivalent_inductance = 0
    
    # We can add the inductor values directly
    for inductor in inductances:
        equivalent_inductance += inductor
    
    return equivalent_inductance

# Function for calculating the power of an inductor. We use the following values:
# - inductance = Inductor value in Henries
# - previous_current = The starting current
# - intant_current = Instanteneous current in a given time
# - previous_time = The starting time
# - time = The final time
def calculate_inductor_power(inductance, previous_current, instant_current, previous_time, time):
    
    # Substraction of the current difference: Final_current - Starting_current
    inductor_current = instant_current - previous_current
    
    # Substraction of the time difference: Final_time - Starting_time
    inductor_time = time - previous_time
    
    # Apply the inductor voltage formula
    inductor_voltage = inductance * (inductor_current/inductor_time)
    
    # Use the calculated current and voltage to obtain the inductor's power (p=vi)
    inductor_power = inductor_voltage * inductor_current
    
    return inductor_power

#----------------------------------------------------------------------------------
# CAPACITORS FORMULAS
#----------------------------------------------------------------------------------

# Function for calculating the current of a capacitor. The values:
# - Capacitance = Capacitor value in Farads
# - previous_voltage = Initial voltage
# - voltage = Final voltage
# - previous_time = Starting time
# - time = Final Time 
def calcuate_capacitor_current(capacitance, previous_voltage, voltage, previous_time, time):
    
    # Calculate the voltage difference = final_voltage - starting_voltage
    capacitor_voltage = voltage - previous_voltage 
    
    # Calculate the the time difference = final_time - starting_time
    capacitor_time = time - previous_time
    
    # Calculate the capacitor current based on the voltage and time value
    capacitor_current = capacitance * (capacitor_voltage/capacitor_time)
    
    return capacitor_current

# Function for calculating the equivalent resistance of a capacitor. It is done as the inverse of a resistor
# Capacitors in series are calculated like resistors in parallel
def calculate_eqc_series(capacitances):
    equivalent_capacitance = 0
    
    # Add the capacitor values in fractions
    for capacitor in capacitances:
        equivalent_capacitance += 1/capacitor
    
    # Raise the obtained value to the power of -1
    equivalent_capacitance **= -1
    
    return equivalent_capacitance

# Function for calculating the equivalnet resistance of a capacitor.
# Capacitors in parallel are calculated like resistors in series.
def calculate_eqc_parallel(capacitances):
    equivalent_capacitance = 0
    
    # We can add the capacitor values directly
    for capacitor in capacitances:
        equivalent_capacitance += capacitor
    
    return equivalent_capacitance

# Function for calculating the power of a capacitor. We use the following values:
# - capacitance = Capacitor value in Farads
# - previous_voltage = The starting voltage
# - intant_voltage = Instanteneous voltage in a given time
# - previous_time = The starting time
# - time = The final time
def calculate_capacitor_power(capacitance, previous_voltage, isntant_voltage, previous_time, time):

    # Calculating voltage difference = final_voltage - initial_voltage
    capacitor_voltage = isntant_voltage - previous_voltage
    
    # Calculating time difference = final_time - initial_time
    capacitor_time = time - previous_time
    
    # Apply the capacitor's current formula
    capacitor_current = capacitance * (capacitor_voltage/capacitor_time)
    
    # Use the calculated current and voltage to obtain the capacitor's power (p=vi)
    capacitor_power = capacitor_voltage * capacitor_current
    
    return capacitor_power