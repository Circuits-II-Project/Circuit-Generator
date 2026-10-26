"""Terminal interface for validated formula calculations."""

from __future__ import annotations

from formula_service import (
    FORMULAS,
    Formula,
    calculate_formula,
    has_valid_time_interval,
    number_matches_rule,
    parse_finite_number,
    parse_positive_list,
)


def show_formula_menu() -> None:
    print("\n--- Fórmulas disponibles ---")
    for option, (name, _) in FORMULAS.items():
        print(f"{option}. {name}")


def choose_formula() -> tuple[str, Formula]:
    while True:
        option = input("\nElige una fórmula: ")
        if option in FORMULAS:
            return option, FORMULAS[option]
        print("Elige uno de los números que aparecen en el menú.")


def read_scalar(field: str, rule: str) -> float:
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
    while True:
        numbers = parse_positive_list(input(f"{field}: "))
        if numbers is not None:
            return numbers
        print(f"{field} necesita una lista de números mayores que cero.")


def collect_formula_values(formula: Formula) -> dict[str, float | list[float]]:
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


def show_collected_values(formula: Formula, values: dict[str, float | list[float]]) -> None:
    name, _ = formula
    print(f"\nFórmula seleccionada: {name}")
    print("Valores ingresados:")
    for field, value in values.items():
        print(f"{field}: {value}")


def show_calculation_results(results: dict[str, float]) -> None:
    print("\nResultados del cálculo:")
    for name, value in results.items():
        print(f"{name}: {value}")


def main() -> None:
    """Run the menu, collect validated values, and show its calculation result."""
    show_formula_menu()
    option, formula = choose_formula()
    values = collect_formula_values(formula)
    show_collected_values(formula, values)
    try:
        results = calculate_formula(option, values)
    except (ZeroDivisionError, ValueError, OverflowError) as error:
        print(f"Error de cálculo: {error}")
        return
    show_calculation_results(results)
