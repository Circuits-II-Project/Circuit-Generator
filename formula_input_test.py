# Menú simple para juntar los datos de una fórmula sin calcularla todavía.

from __future__ import annotations


Formula = tuple[str, tuple[str, ...], tuple[str, ...]]

# Cada opción guarda: nombre que verá el usuario, campos normales y campos lista.
FORMULAS: dict[str, Formula] = {
    "1": ("DC / Basic - Resistor voltage", ("current", "resistance"), ()),
    "2": ("DC / Basic - Resistor current", ("voltage", "resistance"), ()),
    "3": ("DC / Basic - Resistor power", ("current", "voltage"), ()),
    "4": ("DC / Basic - Equivalent resistance series", ("resistances",), ("resistances",)),
    "5": ("DC / Basic - Equivalent resistance parallel", ("resistances",), ("resistances",)),
    "6": ("DC / Inductor - Inductor voltage", ("inductance", "previous_current", "current", "previous_time", "time"), ()),
    "7": ("DC / Inductor - Equivalent inductance series", ("inductances",), ("inductances",)),
    "8": ("DC / Inductor - Equivalent inductance parallel", ("inductances",), ("inductances",)),
    "9": ("DC / Inductor - Inductor power", ("inductance", "previous_current", "instant_current", "previous_time", "time"), ()),
    "10": ("DC / Capacitor - Capacitor current", ("capacitance", "previous_voltage", "voltage", "previous_time", "time"), ()),
    "11": ("DC / Capacitor - Equivalent capacitance series", ("capacitances",), ("capacitances",)),
    "12": ("DC / Capacitor - Equivalent capacitance parallel", ("capacitances",), ("capacitances",)),
    "13": ("DC / Capacitor - Capacitor power", ("capacitance", "previous_voltage", "instant_voltage", "previous_time", "time"), ()),
    "14": ("AC - Rectangular to polar", ("real", "imaginary"), ()),
    "15": ("AC - Polar to rectangular", ("magnitude", "angle_degrees"), ()),
    "16": ("AC - Impedance", ("XC", "XL", "resistor"), ()),
    "17": ("AC - Capacitive reactance", ("capacitance", "source_frequency"), ()),
    "18": ("AC - Inductive reactance", ("inductance", "source_frequency"), ()),
}


def show_formula_menu() -> None:
    # Muestra todas las fórmulas disponibles sin ejecutar ninguna.

    print("\n--- Fórmulas disponibles ---")

    for option, (name, _, _) in FORMULAS.items():
        print(f"{option}. {name}")


def choose_formula() -> tuple[str, Formula]:
    # Solo revisamos que exista una opción; los valores siguen siendo texto en este paso.

    while True:
        option = input("\nElige una fórmula: ")

        if option in FORMULAS:
            return option, FORMULAS[option]

        print("Elige uno de los números que aparecen en el menú.")


def collect_formula_values(formula: Formula) -> dict[str, str | list[str]]:
    # Guarda listas como textos separados por comas; aún no convierte a números.

    _, fields, list_fields = formula
    values: dict[str, str | list[str]] = {}

    for field in fields:
        value = input(f"{field}: ")

        if field in list_fields:
            values[field] = [item.strip() for item in value.split(",")]
        else:
            values[field] = value

    return values


def show_collected_values(formula: Formula, values: dict[str, str | list[str]]) -> None:
    # Por ahora solo mostramos los datos. El cálculo llegará en el siguiente paso.

    name, _, _ = formula
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
