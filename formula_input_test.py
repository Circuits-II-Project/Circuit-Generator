# Menú simple para juntar y revisar los datos de una fórmula antes de calcularla.

from __future__ import annotations

from input_validation import is_valid_number


Field = tuple[str, str]
Formula = tuple[str, tuple[Field, ...]]

# Cada campo también guarda la regla que le toca. Así el menú sabe qué pedir,
# pero las funciones de las fórmulas siguen separadas de este archivo.
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
    # Convertimos primero y usamos la regla compartida para descartar NaN e infinito.

    if not value.strip():
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if is_valid_number(number) else None


def number_matches_rule(number: float, rule: str) -> bool:
    # Los valores signed pueden ser positivos, negativos o cero.

    if rule == "positive":
        return number > 0

    if rule == "non_negative":
        return number >= 0

    return rule == "signed"


def parse_positive_list(value: str) -> list[float] | None:
    # Una coma sin un valor también cuenta como un dato incompleto.

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
    # El segundo momento tiene que venir después del primero.

    return time > previous_time


def show_formula_menu() -> None:
    # Muestra todas las fórmulas disponibles sin ejecutar ninguna.

    print("\n--- Fórmulas disponibles ---")

    for option, (name, _) in FORMULAS.items():
        print(f"{option}. {name}")


def choose_formula() -> tuple[str, Formula]:
    # Solo revisamos que exista una opción antes de pedir sus valores.

    while True:
        option = input("\nElige una fórmula: ")

        if option in FORMULAS:
            return option, FORMULAS[option]

        print("Elige uno de los números que aparecen en el menú.")


def read_scalar(field: str, rule: str) -> float:
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
    # Las listas se escriben con comas, por ejemplo: 10, 20, 30.

    while True:
        numbers = parse_positive_list(input(f"{field}: "))

        if numbers is not None:
            return numbers

        print(f"{field} necesita una lista de números mayores que cero.")


def collect_formula_values(formula: Formula) -> dict[str, float | list[float]]:
    # Aquí ya guardamos números de verdad, pero todavía no llamamos a ninguna fórmula.

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


def main() -> None:
    # Junta la opción y sus valores, pero no llama a ninguna fórmula todavía.

    show_formula_menu()
    _, formula = choose_formula()
    values = collect_formula_values(formula)
    show_collected_values(formula, values)


if __name__ == "__main__":
    main()
