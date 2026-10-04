# Menú simple para juntar y revisar los datos de una fórmula antes de calcularla.

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

# FORMULAS describe las opciones del menú, los datos que pide cada una y su regla.
# Las ecuaciones eléctricas siguen en AC_behavior_test.py y DC_behavior_test.py
# para no duplicar la lógica matemática en la parte que conversa con el usuario.
FORMULAS: dict[str, Formula] = {
    "1": (
        "DC / Basic - Resistor voltage",
        (("current", "signed"), ("resistance", "positive")),
    ),
    "2": (
        "DC / Basic - Resistor current",
        (("voltage", "signed"), ("resistance", "positive")),
    ),
    "3": (
        "DC / Basic - Resistor power",
        (("current", "signed"), ("voltage", "signed")),
    ),
    "4": (
        "DC / Basic - Equivalent resistance series",
        (("resistances", "positive_list"),),
    ),
    "5": (
        "DC / Basic - Equivalent resistance parallel",
        (("resistances", "positive_list"),),
    ),
    "6": (
        "DC / Inductor - Inductor voltage",
        (
            ("inductance", "positive"),
            ("previous_current", "signed"),
            ("current", "signed"),
            ("previous_time", "non_negative"),
            ("time", "non_negative"),
        ),
    ),
    "7": (
        "DC / Inductor - Equivalent inductance series",
        (("inductances", "positive_list"),),
    ),
    "8": (
        "DC / Inductor - Equivalent inductance parallel",
        (("inductances", "positive_list"),),
    ),
    "9": (
        "DC / Inductor - Inductor power",
        (
            ("inductance", "positive"),
            ("previous_current", "signed"),
            ("instant_current", "signed"),
            ("previous_time", "non_negative"),
            ("time", "non_negative"),
        ),
    ),
    "10": (
        "DC / Capacitor - Capacitor current",
        (
            ("capacitance", "positive"),
            ("previous_voltage", "signed"),
            ("voltage", "signed"),
            ("previous_time", "non_negative"),
            ("time", "non_negative"),
        ),
    ),
    "11": (
        "DC / Capacitor - Equivalent capacitance series",
        (("capacitances", "positive_list"),),
    ),
    "12": (
        "DC / Capacitor - Equivalent capacitance parallel",
        (("capacitances", "positive_list"),),
    ),
    "13": (
        "DC / Capacitor - Capacitor power",
        (
            ("capacitance", "positive"),
            ("previous_voltage", "signed"),
            ("instant_voltage", "signed"),
            ("previous_time", "non_negative"),
            ("time", "non_negative"),
        ),
    ),
    "14": ("AC - Rectangular to polar", (("real", "signed"), ("imaginary", "signed"))),
    "15": (
        "AC - Polar to rectangular",
        (("magnitude", "non_negative"), ("angle_degrees", "signed")),
    ),
    "16": (
        "AC - Impedance",
        (("XC", "non_negative"), ("XL", "non_negative"), ("resistor", "positive")),
    ),
    "17": (
        "AC - Capacitive reactance",
        (("capacitance", "positive"), ("source_frequency", "positive")),
    ),
    "18": (
        "AC - Inductive reactance",
        (("inductance", "positive"), ("source_frequency", "positive")),
    ),
}


def parse_finite_number(value: str) -> float | None:
    """Convierte texto en un número finito o devuelve None."""

    # Reutilizamos is_valid_number para que NaN e infinito sigan la misma regla
    # de seguridad numérica que usa el resto del proyecto.

    if not value.strip():
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if is_valid_number(number) else None


def number_matches_rule(number: float, rule: str) -> bool:
    """Indica si un número cumple la regla pedida por un campo."""

    # signed acepta cualquier número finito, incluido negativo y cero.
    # positive exige más de cero, y non_negative deja pasar cero pero no negativos.

    if rule == "positive":
        return number > 0

    if rule == "non_negative":
        return number >= 0

    return rule == "signed"


def parse_positive_list(value: str) -> list[float] | None:
    """Convierte una lista con comas si todos sus valores son finitos y positivos."""

    # positive_list necesita al menos un dato y no permite valores vacíos, cero
    # ni negativos, para no pasar una lista medio válida a una fórmula equivalente.

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
    """Comprueba que el segundo instante sea posterior al primero."""

    return time > previous_time


def show_formula_menu() -> None:
    # Muestra todas las fórmulas disponibles sin ejecutar ninguna.

    print("\n--- Fórmulas disponibles ---")

    for option, (name, _) in FORMULAS.items():
        print(f"{option}. {name}")


def choose_formula() -> tuple[str, Formula]:
    """Pide una opción del menú hasta que el usuario elija una existente."""

    # Solo revisamos que exista una opción antes de pedir sus valores.

    while True:
        option = input("\nElige una fórmula: ")

        if option in FORMULAS:
            return option, FORMULAS[option]

        print("Elige uno de los números que aparecen en el menú.")


def read_scalar(field: str, rule: str) -> float:
    """Lee y repite un valor numérico hasta que cumpla su regla."""

    # Si el dato no sirve, repetimos este mismo campo sin reiniciar todo el menú.

    while True:
        number = parse_finite_number(input(f"{field}: "))

        if number is not None and number_matches_rule(number, rule):
            return number

        if rule == "positive":
            print(f"{field} debe ser un número mayor que cero.")
        elif rule == "non_negative":
            print(f"{field} debe ser un número mayor o igual a cero.")
        else:
            print(f"{field} debe ser un número finito.")


def read_positive_list(field: str) -> list[float]:
    """Lee una lista positiva separada por comas y la repite si falla."""

    # Las listas se escriben con comas, por ejemplo: 10, 20, 30.

    while True:
        numbers = parse_positive_list(input(f"{field}: "))

        if numbers is not None:
            return numbers

        print(f"{field} necesita una lista de números mayores que cero.")


def collect_formula_values(formula: Formula) -> dict[str, float | list[float]]:
    """Recoge los valores de una fórmula y los devuelve ya validados."""

    # Aquí guardamos números de verdad. El cálculo queda separado para que estas
    # reglas de entrada no se mezclen ni se repitan dentro de las fórmulas.

    _, fields = formula
    values: dict[str, float | list[float]] = {}

    for field, rule in fields:
        if rule == "positive_list":
            values[field] = read_positive_list(field)
            continue

        while True:
            number = read_scalar(field, rule)
            previous_time = values.get("previous_time")

            if (
                field != "time"
                or not isinstance(previous_time, float)
                or has_valid_time_interval(previous_time, number)
            ):
                values[field] = number
                break

            print("time debe ser mayor que previous_time.")

    return values


def show_collected_values(
    formula: Formula,
    values: dict[str, float | list[float]],
) -> None:
    # Por ahora solo mostramos los datos ya revisados; el cálculo llega después.

    name, _ = formula
    print(f"\nFórmula seleccionada: {name}")
    print("Valores ingresados:")

    for field, value in values.items():
        print(f"{field}: {value}")


def calculate_formula(
    option: str,
    values: dict[str, float | list[float]],
) -> dict[str, float]:
    """Envía valores ya validados a la fórmula de circuito seleccionada."""

    # Step 2 ya revisó estos datos. Esta función no los valida ni repite ecuaciones:
    # solo enruta cada opción a la función DC o AC existente y devuelve sus resultados
    # en un diccionario para que otras partes del programa puedan reutilizarlos después.

    if option == "1":
        return {
            "resistor_voltage": calculate_resistor_voltage(
                values["current"],
                values["resistance"],
            )
        }
    if option == "2":
        return {
            "resistor_current": calculate_resistor_current(
                values["voltage"],
                values["resistance"],
            )
        }
    if option == "3":
        return {
            "resistor_power": calculate_resistor_power(
                values["current"],
                values["voltage"],
            )
        }
    if option == "4":
        return {"equivalent_resistance": calculate_eqr_series(values["resistances"])}
    if option == "5":
        return {
            "equivalent_resistance": calculate_eqr_parallel(values["resistances"])
        }
    if option == "6":
        return {
            "inductor_voltage": calculate_inductor_voltage(
                values["inductance"],
                values["previous_current"],
                values["current"],
                values["previous_time"],
                values["time"],
            )
        }
    if option == "7":
        return {"equivalent_inductance": calculate_eqi_series(values["inductances"])}
    if option == "8":
        return {
            "equivalent_inductance": calculate_eqi_parallel(values["inductances"])
        }
    if option == "9":
        return {
            "inductor_power": calculate_inductor_power(
                values["inductance"],
                values["previous_current"],
                values["instant_current"],
                values["previous_time"],
                values["time"],
            )
        }
    if option == "10":
        return {
            "capacitor_current": calculate_capacitor_current(
                values["capacitance"],
                values["previous_voltage"],
                values["voltage"],
                values["previous_time"],
                values["time"],
            )
        }
    if option == "11":
        return {"equivalent_capacitance": calculate_eqc_series(values["capacitances"])}
    if option == "12":
        return {
            "equivalent_capacitance": calculate_eqc_parallel(values["capacitances"])
        }
    if option == "13":
        return {
            "capacitor_power": calculate_capacitor_power(
                values["capacitance"],
                values["previous_voltage"],
                values["instant_voltage"],
                values["previous_time"],
                values["time"],
            )
        }
    if option == "14":
        magnitude, angle_degrees = rec_to_pol(values["real"], values["imaginary"])
        return {"magnitude": magnitude, "angle_degrees": angle_degrees}
    if option == "15":
        real, imaginary = pol_to_rec(values["magnitude"], values["angle_degrees"])
        return {"real": real, "imaginary": imaginary}
    if option == "16":
        impedance, phase_angle = calc_impedance(
            values["XC"],
            values["XL"],
            values["resistor"],
        )
        return {"total_impedance": impedance, "phase_angle": phase_angle}
    if option == "17":
        return {
            "capacitive_reactance": calc_capacitive_reactance(
                values["capacitance"],
                values["source_frequency"],
            )
        }
    if option == "18":
        return {
            "inductive_reactance": calc_inductive_reactance(
                values["inductance"],
                values["source_frequency"],
            )
        }

    raise ValueError("Unsupported formula selection.")


def show_calculation_results(results: dict[str, float]) -> None:
    """Muestra en consola los resultados devueltos por un cálculo."""

    # Los resultados se muestran aparte para que calculate_formula no imprima nada.

    print("\nResultados del cálculo:")

    for name, value in results.items():
        print(f"{name}: {value}")


def main() -> None:
    # El flujo de consola es: menú, datos validados, cálculo y resultado mostrado.

    show_formula_menu()
    option, formula = choose_formula()
    values = collect_formula_values(formula)
    show_collected_values(formula, values)

    # Solo atrapamos errores esperables de cálculo para cerrar este intento con calma.
    # Los demás errores quedan visibles porque normalmente son bugs reales.

    try:
        results = calculate_formula(option, values)
    except (ZeroDivisionError, ValueError, OverflowError) as error:
        print(f"Error de cálculo: {error}")
        return

    show_calculation_results(results)

if __name__ == "__main__":
    main()
