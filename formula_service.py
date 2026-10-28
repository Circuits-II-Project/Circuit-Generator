"""Validated formula selection and calculation services without terminal I/O."""

from __future__ import annotations

from AC_behavior_test import (
    calc_capacitive_reactance,
    calc_impedance,
    calc_inductive_reactance,
    pol_to_rec,
    rec_to_pol,
)
from DC_behavior_test import (
    calculate_capacitor_current,
    calculate_capacitor_power,
    calculate_eqc_parallel,
    calculate_eqc_series,
    calculate_eqi_parallel,
    calculate_eqi_series,
    calculate_eqr_parallel,
    calculate_eqr_series,
    calculate_inductor_power,
    calculate_inductor_voltage,
    calculate_resistor_current,
    calculate_resistor_power,
    calculate_resistor_voltage,
)
from input_validation import is_valid_number


Field = tuple[str, str]
Formula = tuple[str, tuple[Field, ...]]


FORMULAS: dict[str, Formula] = {
    "1": ("DC / Basic - Resistor voltage", (("current", "signed"), ("resistance", "positive"))),
    "2": ("DC / Basic - Resistor current", (("voltage", "signed"), ("resistance", "positive"))),
    "3": ("DC / Basic - Resistor power", (("current", "signed"), ("voltage", "signed"))),
    "4": ("DC / Basic - Equivalent resistance series", (("resistances", "positive_list"),)),
    "5": ("DC / Basic - Equivalent resistance parallel", (("resistances", "positive_list"),)),
    "6": ("DC / Inductor - Inductor voltage", (("inductance", "positive"), ("previous_current", "signed"), ("current", "signed"), ("previous_time", "non_negative"), ("time", "non_negative"))),
    "7": ("DC / Inductor - Equivalent inductance series", (("inductances", "positive_list"),)),
    "8": ("DC / Inductor - Equivalent inductance parallel", (("inductances", "positive_list"),)),
    "9": ("DC / Inductor - Inductor power", (("inductance", "positive"), ("previous_current", "signed"), ("instant_current", "signed"), ("previous_time", "non_negative"), ("time", "non_negative"))),
    "10": ("DC / Capacitor - Capacitor current", (("capacitance", "positive"), ("previous_voltage", "signed"), ("voltage", "signed"), ("previous_time", "non_negative"), ("time", "non_negative"))),
    "11": ("DC / Capacitor - Equivalent capacitance series", (("capacitances", "positive_list"),)),
    "12": ("DC / Capacitor - Equivalent capacitance parallel", (("capacitances", "positive_list"),)),
    "13": ("DC / Capacitor - Capacitor power", (("capacitance", "positive"), ("previous_voltage", "signed"), ("instant_voltage", "signed"), ("previous_time", "non_negative"), ("time", "non_negative"))),
    "14": ("AC - Rectangular to polar", (("real", "signed"), ("imaginary", "signed"))),
    "15": ("AC - Polar to rectangular", (("magnitude", "non_negative"), ("angle_degrees", "signed"))),
    "16": ("AC - Impedance", (("XC", "non_negative"), ("XL", "non_negative"), ("resistor", "positive"))),
    "17": ("AC - Capacitive reactance", (("capacitance", "positive"), ("source_frequency", "positive"))),
    "18": ("AC - Inductive reactance", (("inductance", "positive"), ("source_frequency", "positive"))),
}


def parse_finite_number(value: str) -> float | None:
    """Convert text to a finite number, or return None."""
    if not value.strip():
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if is_valid_number(number) else None


def number_matches_rule(number: float, rule: str) -> bool:
    """Return whether a number satisfies a formula field rule."""
    if rule == "positive":
        return number > 0
    if rule == "non_negative":
        return number >= 0
    return rule == "signed"


def parse_positive_list(value: str) -> list[float] | None:
    """Convert a comma-separated list of finite positive numbers."""
    if not value.strip():
        return None
    items = [item.strip() for item in value.split(",")]
    if any(not item for item in items):
        return None
    numbers = [parse_finite_number(item) for item in items]
    if any(number is None or number <= 0 for number in numbers):
        return None
    return [number for number in numbers if number is not None]


def has_valid_time_interval(previous_time: float, time: float) -> bool:
    """Return whether the final time is after the previous time."""
    return time > previous_time


def calculate_formula(
    option: str,
    values: dict[str, float | list[float]],
) -> dict[str, float]:
    """Route already validated values to the selected existing DC or AC formula."""
    if option == "1":
        return {"resistor_voltage": calculate_resistor_voltage(values["current"], values["resistance"])}
    if option == "2":
        return {"resistor_current": calculate_resistor_current(values["voltage"], values["resistance"])}
    if option == "3":
        return {"resistor_power": calculate_resistor_power(values["current"], values["voltage"])}
    if option == "4":
        return {"equivalent_resistance": calculate_eqr_series(values["resistances"])}
    if option == "5":
        return {"equivalent_resistance": calculate_eqr_parallel(values["resistances"])}
    if option == "6":
        return {"inductor_voltage": calculate_inductor_voltage(values["inductance"], values["previous_current"], values["current"], values["previous_time"], values["time"])}
    if option == "7":
        return {"equivalent_inductance": calculate_eqi_series(values["inductances"])}
    if option == "8":
        return {"equivalent_inductance": calculate_eqi_parallel(values["inductances"])}
    if option == "9":
        return {"inductor_power": calculate_inductor_power(values["inductance"], values["previous_current"], values["instant_current"], values["previous_time"], values["time"])}
    if option == "10":
        return {"capacitor_current": calculate_capacitor_current(values["capacitance"], values["previous_voltage"], values["voltage"], values["previous_time"], values["time"])}
    if option == "11":
        return {"equivalent_capacitance": calculate_eqc_series(values["capacitances"])}
    if option == "12":
        return {"equivalent_capacitance": calculate_eqc_parallel(values["capacitances"])}
    if option == "13":
        return {"capacitor_power": calculate_capacitor_power(values["capacitance"], values["previous_voltage"], values["instant_voltage"], values["previous_time"], values["time"])}
    if option == "14":
        magnitude, angle_degrees = rec_to_pol(values["real"], values["imaginary"])
        return {"magnitude": magnitude, "angle_degrees": angle_degrees}
    if option == "15":
        real, imaginary = pol_to_rec(values["magnitude"], values["angle_degrees"])
        return {"real": real, "imaginary": imaginary}
    if option == "16":
        impedance, phase_angle = calc_impedance(values["XC"], values["XL"], values["resistor"])
        return {"total_impedance": impedance, "phase_angle": phase_angle}
    if option == "17":
        return {"capacitive_reactance": calc_capacitive_reactance(values["capacitance"], values["source_frequency"])}
    if option == "18":
        return {"inductive_reactance": calc_inductive_reactance(values["inductance"], values["source_frequency"])}
    raise ValueError("Unsupported formula selection.")
