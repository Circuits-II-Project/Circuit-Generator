import os
# Wipes the terminal screen completely clean before printing anything else
os.system('cls' if os.name == 'nt' else 'clear')

def calculate_resistor_voltage(current, resistance):
    resistor_voltage = current * resistance
    
    return resistor_voltage

def calculate_resistor_current(voltage, resistance):
    resistor_current = voltage/resistance
    
    return resistor_current

def calculate_resistor_power(current, voltage):
    resistor_power = current * voltage
    
    return resistor_power
    
def calculate_eqr_parallel(resistances):
    equivalent_resistance = 0
    
    for resistor in resistances:
        equivalent_resistance += 1/resistor
        
    equivalent_resistance **= -1
    
    return equivalent_resistance

def calculate_eqr_series(resistances):
    equivalent_resistance = 0
    
    for resistor in resistances:
        equivalent_resistance += resistor
    
    return equivalent_resistance


#------------------------------------------------------------------------------------------------------#

def calculate_inductor_voltage(inductance, previous_current, current, previous_time, time):
    inductor_current = current - previous_current
    inductor_time = time - previous_time
    
    inductor_voltage = inductance *(inductor_current/inductor_time)
    
    return inductor_voltage

def calculate_eqi_parallel(inductances):
    equivalent_inductance = 0
        
    for inductor in inductances:
        equivalent_inductance += 1/inductor
        
    equivalent_inductance **= -1
    
    return equivalent_inductance

def calculate_eqi_series(inductances):
    equivalent_inductance = 0
    
    for inductor in inductances:
        equivalent_inductance += inductor
    
    return equivalent_inductance

def calculate_inductor_power(inductance_current, previous_current, current, previous_time, time):
    inductor_current = current - previous_current
    inductor_time = time - previous_time
        
    inductor_power = inductance_current *(inductor_current/inductor_time)
    
    return inductor_power

#------------------------------------------------------------------------------------------------------#

def calcuate_capacitor_current(capacitance, previous_voltage, voltage, previous_time, time):
    capacitor_voltage = previous_voltage - voltage
    capacitor_time = previous_time - time
    
    capacitor_current = capacitance * (capacitor_voltage/capacitor_time)
    
    return capacitor_current

def calculate_eqc_series(capacitances):
    equivalent_capacitance = 0
        
    for capacitor in capacitances:
        equivalent_capacitance += 1/capacitor
        
    equivalent_capacitance **= -1
    
    return equivalent_capacitance

def calculate_eqc_parallel(capacitances):
    equivalent_capacitance = 0
    
    for capacitor in capacitances:
        equivalent_capacitance += capacitor
    
    return equivalent_capacitance

#------------------------------------------------------------------------------------------------------#
print("Voltage Source = 25")
print("-" * 80)
print("Resistors in Series")
print("-" * 80)
print("R1 = 100 | R2 = 150 | R3 = 50")
print("-" * 80)

voltage_source = 25

R1 = 100
R2 = 150
R3 = 50
resistors = [R1, R2, R3]

equivalent_resistance = calculate_eqr_series(resistors)
print(f"Equivalent Resistance: {equivalent_resistance}")

total_current = voltage_source/equivalent_resistance

R1_voltage = calculate_resistor_voltage(total_current, R1)
R2_voltage = calculate_resistor_voltage(total_current, R2)
R3_voltage = calculate_resistor_voltage(total_current, R3)

print("-" * 80)
print("Resistor Voltage")
print("-" * 80)
print(f"V1 = {R1_voltage:.2f}")
print(f"V2 = {R2_voltage:.2f}")
print(f"V3 = {R3_voltage:.2f}")

print(f"{R1_voltage + R2_voltage + R3_voltage}")

print("_" *80)

print("Capacitors in Series")
print("-" * 80)
print("C1 = 10 | C2 = 5 | R3 = 0.5")
print
print("-" * 80)

C1 = 10
C2 = 5
C3 = 0.5
capacitors = [C1, C2, C3]

equivalent_capacitance = calculate_eqc_series(capacitors)
print(f"Equivalent Capacitance: {equivalent_capacitance}")

print("_" * 80)

print("Inductors in Series")
print("-" * 80)
print("L1 = 10 | L2 = 5 | L3 = 0.5")
print
print("-" * 80)

L1 = 10
L2 = 5
L3 = 0.5
inductors = [L1, L2, L3]

equivalent_inductance = calculate_eqi_series(inductors)
print(f"Equivalent Inductance: {equivalent_inductance}")

print("_" * 80 + "\n\n")

print("RL Circuit")

print("Voltage Source: 10V")
print("Two Resistors in series and an inductor in series")
print("R1 = 150 | R2 = 200 | L1 = 1")
print("Starting Time: 0 | Final Time: 5")
print("-" * 80)
voltage_source = 10
R1 = 150
R2 = 200
L1 = 1

resistors = [R1, R2]
equivalent_resistance = calculate_eqr_series(resistors)
total_current = voltage_source/equivalent_resistance
start_time = 0
final_time = 5

L1_voltage = calculate_inductor_voltage(L1, 0, total_current, start_time, final_time)

R1_voltage = calculate_resistor_voltage(total_current, R1)
R2_voltage = calculate_resistor_voltage(total_current, R2)

print(f"Equivalent Resistance: {equivalent_resistance:.2f}")
print(f"Total Current: {total_current:.2f}")
print(f"R1 Voltage:{R1_voltage:.2f}")
print(f"R2 Voltage:{R2_voltage:.2f}")
print(f"Inductor Voltage: {L1_voltage:.2f}")
print(f"Recalculated Voltage: {round(R1_voltage + R2_voltage + L1_voltage)}V")
print("-" * 80)