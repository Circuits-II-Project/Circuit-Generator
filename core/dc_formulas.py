import os

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
    inductor_power = inductor_voltage * instant_current
    
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
def calculate_capacitor_current(capacitance, previous_voltage, voltage, previous_time, time):
    
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
    capacitor_power = isntant_voltage * capacitor_current
    
    return capacitor_power

if __name__ == "__main__":
    # Las demostraciones quedan aquí para que importar las fórmulas no las ejecute.
    os.system('cls' if os.name == 'nt' else 'clear')

    #-----------------------------------------------------------------------------------------------------
    # RESISTOR TEST
    #-----------------------------------------------------------------------------------------------------
    #Test for the resistor voltage formula
    Resistor_voltage = calculate_resistor_voltage(0.005, 100)
    print("Current: 0.005A | Resistance: 100 Ohms")
    print(f"Resistor Voltage: {Resistor_voltage}V")
    print()

    #Test for the resistor current formula
    Resistor_current = calculate_resistor_current(0.5, 100)
    print("Voltage: 0.5V | Resistance: 100 Ohms")
    print(f"Resistor Current: {Resistor_current}A")
    print()

    #Test for the resistor power formula
    Resistor_power = calculate_resistor_power(0.005, 0.5)
    print("Voltage: 0.5V | Current: 0.005A")
    print(f"Resistor Power: {Resistor_current}W")
    print()

    #Test for the equivalent resistance of parallel resistors
    Resistors_parallel = [100, 50, 100, 15]
    Equivalent_parallel_resistance = calculate_eqr_parallel(Resistors_parallel)
    print("R1 = 100 ohms | R2 = 50 ohms | R3 = 100 ohms | R4 = 15 ohms")
    print(f"Equivalent Resistance: {Equivalent_parallel_resistance} Ohms")
    print()

    #Test for the equivalent resistance of series resistors
    Resistors_series = [100, 50, 100, 15]
    Equivalent_series_resistance = calculate_eqr_series(Resistors_series)
    print("R1 = 100 ohms | R2 = 50 ohms | R3 = 100 ohms | R4 = 15 ohms")
    print(f"Equivalent Resistance: {Equivalent_series_resistance} Ohms")
    print()

    #-----------------------------------------------------------------------------------------------------
    # INDUCTOR TEST
    #-----------------------------------------------------------------------------------------------------
    #Test for the voltage in an inductor
    inductance = 0.015
    start_current = 0.005
    final_current = 0.1
    start_time = 0 #Would be constant
    final_time = 1
    Inductor_voltage = calculate_inductor_voltage(inductance, start_current, final_current, start_time, final_time)
    print("Inductance = 15mH | Starting Current = 5mA | Final Current = 4mA | Start time = 10ms | Final Time = 1s")
    print(f"Inductor Voltage: {Inductor_voltage} V")
    print()

    #Test for the equivalent inductance of parallel inductors
    Inductors_parallel = [0.015, 0.05, 0.01, 0.001]
    Equivalent_parallel_inductance = calculate_eqi_parallel(Inductors_parallel)
    print("R1 = 15mH | R2 = 50 mH | R3 = 10mH | R4 = 1mH")
    print(f"Equivalent Inductance: {Equivalent_parallel_inductance} H")
    print()

    #Test for the equivalent inductance of series inductors
    Inductors_series = [0.015, 0.05, 0.01, 0.001]
    Equivalent_series_inductance = calculate_eqi_series(Inductors_series)
    print("R1 = 15mH | R2 = 50 mH | R3 = 10mH | R4 = 1mH")
    print(f"Equivalent Inductance: {Equivalent_series_inductance} H")
    print()

    #Test for the power in an inductor
    inductance = 0.015
    start_current = 0.005
    final_current = 0.1
    start_time = 0 #Would be constant
    final_time = 1
    Inductor_power = calculate_inductor_power(inductance, start_current, final_current, start_time, final_time)
    print("Inductance = 15mH | Starting Current = 5mA | Final Current = 4mA | Start time = 0s | Final Time = 1s")
    print(f"Inductor Power: {Inductor_voltage} W")
    print()

    #-----------------------------------------------------------------------------------------------------
    # CAPACITOR TEST
    #-----------------------------------------------------------------------------------------------------
    #Test for the current in a capacitor
    capacitance = 0.015
    start_voltage = 15
    final_voltage = 20
    start_time = 0 #Would be constant
    final_time = 1
    Capacitor_current = calculate_capacitor_current(capacitance, start_voltage, final_voltage, start_time, final_time)
    print("capacitance = 15mF | Starting Voltage = 15V | Final Voltage = 20V | Start time = 0s | Final Time = 1s")
    print(f"Capacitor Current: {Capacitor_current} A")
    print()

    #Test for the equivalent capacitance of series capacitors
    Capacitors_series = [15, 5, 1, 10]
    Equivalent_series_capacitance = calculate_eqc_series(Capacitors_series)
    print("R1 = 15F | R2 = 5F | R3 = 1F | R4 = 10F")
    print(f"Equivalent Capacitance: {Equivalent_series_capacitance} F")
    print()

    #Test for the equivalent capacitance of parallel capacitors
    Capacitors_parallel = [15, 5, 1, 10]
    Equivalent_parallel_capacitance = calculate_eqc_parallel(Capacitors_parallel)
    print("R1 = 15F | R2 = 5F | R3 = 1F | R4 = 10F")
    print(f"Equivalent Capacitance: {Equivalent_parallel_capacitance} F")
    print()

    #Test for the power in a capacitor
    capacitance = 0.015
    start_voltage = 15
    final_voltage = 20
    start_time = 0 #Would be constant
    final_time = 1
    Capacitor_power = calculate_capacitor_power(capacitance, start_voltage, final_voltage, start_time, final_time)
    print("capacitance = 15mF | Starting Voltage = 15V | Final Voltage = 20V | Start time = 0s | Final Time = 1s")
    print(f"Capacitor Power: {Capacitor_power} W")
    print()
