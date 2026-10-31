"""Terminal interface for validated formula calculations."""

from __future__ import annotations

from pathlib import Path

from formula_service import (
    FORMULAS,
    Formula,
    calculate_formula,
    has_valid_time_interval,
    number_matches_rule,
    parse_finite_number,
    parse_positive_list,
)
from formula_storage import StorageFormatError, append_calculation


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


def should_save_calculation() -> bool:
    """Ask whether to save a completed calculation.

    Returns:
        True only when the user explicitly accepts with ``s``. EOF is treated
        as declining so existing piped terminal commands still finish normally.
    """
    while True:
        try:
            response = input("\n¿Deseas guardar este cálculo? (s/n): ").strip().lower()
        except EOFError:
            # Older non-interactive commands end after formula inputs.
            return False

        if response == "s":
            return True
        if response == "n":
            return False
        print("Responde con s para guardar o n para no guardar.")


def main(storage_path: str | Path = "storage.json") -> None:
    """Run one formula calculation and optionally save its completed result.

    Args:
        storage_path: JSON destination used only after the user accepts saving.
    """
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

    if not should_save_calculation():
        return

    formula_name, _ = formula
    try:
        append_calculation(
            storage_path,
            option,
            formula_name,
            values,
            results,
            diagram_path=None,
        )
    except (OSError, StorageFormatError, TypeError, ValueError) as error:
        print(f"No se pudo guardar el cálculo: {error}")
        return

    print("Cálculo guardado correctamente.")
