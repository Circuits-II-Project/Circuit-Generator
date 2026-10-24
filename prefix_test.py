import os

from prefixes import from_prefix, to_prefix
from DC_behavior_test import (
    calculate_resistor_voltage,
    calculate_resistor_power,
    calculate_eqr_series,
    calculate_eqr_parallel,
)
from AC_behavior_test import (
    calc_capacitive_reactance,
    calc_inductive_reactance,
    calc_impedance,
    pol_to_rec,
)

# Function for asking a value until the user types a valid one
def read_value(prompt):
    while True:
        try:
            return from_prefix(input(prompt))
        except ValueError:
            print("Invalid value. Use a number with an optional prefix (p, n, u, m, k, M, G, T). Example: 4.7k")

# Function for asking a list of values separated by commas
def read_values(prompt):
    while True:
        try:
            return [from_prefix(text) for text in input(prompt).split(",")]
        except ValueError:
            print("Invalid list. Separate the values with commas. Example: 1k, 2.2k, 470")

#-----------------------------------------------------------------------------------------------------
# DC TEST
#-----------------------------------------------------------------------------------------------------
def dc_test():
    print("--- DC: Resistor ---")
    current = read_value("Current (e.g. 5m): ")
    resistance = read_value("Resistance (e.g. 1k): ")

    voltage = calculate_resistor_voltage(current, resistance)
    power = calculate_resistor_power(current, voltage)

    print(f"Current = {to_prefix(current, 'A')} | Resistance = {to_prefix(resistance, 'ohm')}")
    print(f"Resistor Voltage: {to_prefix(voltage, 'V')}")
    print(f"Resistor Power: {to_prefix(power, 'W')}")
    print()

    print("--- DC: Equivalent Resistance ---")
    resistors = read_values("Resistors separated by commas (e.g. 1k, 2.2k, 470): ")

    print(f"Series: {to_prefix(calculate_eqr_series(resistors), 'ohm')}")
    print(f"Parallel: {to_prefix(calculate_eqr_parallel(resistors), 'ohm')}")
    print()

#-----------------------------------------------------------------------------------------------------
# AC TEST
#-----------------------------------------------------------------------------------------------------
def ac_test():
    print("--- AC: Series RLC Impedance ---")
    frequency = read_value("Source frequency (e.g. 60, 1k): ")
    resistance = read_value("Resistance (e.g. 100): ")
    capacitance = read_value("Capacitance (e.g. 10u): ")
    inductance = read_value("Inductance (e.g. 50m): ")

    XC = calc_capacitive_reactance(capacitance, frequency)
    XL = calc_inductive_reactance(inductance, frequency)
    Z, angle_degrees = calc_impedance(XC, XL, resistance)
    real, imaginary = pol_to_rec(Z, angle_degrees)

    print(f"XC = {to_prefix(XC, 'ohm')}")
    print(f"XL = {to_prefix(XL, 'ohm')}")
    print(f"Z (polar) = {to_prefix(Z, 'ohm')} at {angle_degrees:.2f} degrees")
    print(f"Z (rectangular) = {to_prefix(real, 'ohm')} + j({to_prefix(imaginary, 'ohm')})")
    print()

if __name__ == "__main__":
    # Wipes the terminal screen completely clean before printing anything else
    os.system('cls' if os.name == 'nt' else 'clear')

    dc_test()
    ac_test()
