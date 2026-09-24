"""Small console program for entering and validating one circuit by hand."""

from __future__ import annotations

from collections.abc import Callable

from input_validation import (
    COMPONENT_ID_PREFIXES,
    COMPONENT_UNITS,
    ENGINEERING_PREFIXES,
    SUPPORTED_CIRCUIT_TYPES,
    is_valid_number,
    validate_circuit,
    validate_nodes,
)


# ---------------------------------------------------------------------------
# Preguntas que revisan cada respuesta al momento
# ---------------------------------------------------------------------------
#
# Este archivo es para probar a mano. Si un dato esta mal, lo avisa y pide ese
# mismo dato otra vez. No guarda ni calcula nada; al final solo llama al
# validador real para confirmar que el circuito completo esta bien.
#

def ask_until_valid(
    message: str,
    check: Callable[[str], str | None],
) -> str:
    """Keep asking until the check says the answer is valid."""

    while True:
        value = input(message)
        error = check(value)

        if error is None:
            return value

        print(f"  Error: {error}\n")


def ask_non_empty(message: str) -> str:
    """Ask for text that contains something besides spaces."""

    def check(value: str) -> str | None:
        if not value.strip():
            return "No puede quedar vacío."
        return None

    return ask_until_valid(message, check)


def ask_choice(message: str, allowed: set[str]) -> str:
    """Ask for one of the allowed options."""

    def check(value: str) -> str | None:
        if value not in allowed:
            return f"Debe ser uno de estos: {', '.join(sorted(allowed))}."
        return None

    return ask_until_valid(message, check)


def ask_number(message: str, must_be_positive: bool = False) -> float:
    """Ask for a normal finite number."""

    def check(value: str) -> str | None:
        try:
            number = float(value)
        except ValueError:
            return "Escribe un número, no texto."

        if not is_valid_number(number):
            return "No puede ser NaN ni infinito."
        if must_be_positive and number <= 0:
            return "Debe ser mayor que cero."
        return None

    return float(ask_until_valid(message, check))


def ask_nodes() -> list[str]:
    """Ask for nodes separated by commas, allowing spaces after commas."""

    def check(value: str) -> str | None:
        nodes = [node.strip() for node in value.split(",")]
        errors = validate_nodes(nodes)
        return errors[0] if errors else None

    value = ask_until_valid("Nodos separados por comas (ejemplo A, B, C): ", check)
    return [node.strip() for node in value.split(",")]


def ask_node(message: str, nodes: list[str], other_node: str | None = None) -> str:
    """Ask for a node that exists and is different from the other endpoint."""

    def check(value: str) -> str | None:
        if value not in nodes:
            return f"{value!r} no está en la lista de nodos."
        if value == other_node:
            return "No puede usar el mismo nodo en los dos extremos."
        return None

    return ask_until_valid(message, check)


def ask_source(nodes: list[str]) -> dict[str, object]:
    """Ask for the one voltage source supported by the project."""

    print("\n--- Fuente de voltaje ---")
    source_id = ask_choice("ID de la fuente (V1): ", {"V1"})
    source_type = ask_choice("Tipo de fuente (AC o DC): ", {"AC", "DC"})
    source_voltage = ask_number("Voltaje: ")

    if source_type == "AC":
        source_frequency: float | None = ask_number("Frecuencia: ", True)
    else:
        source_frequency = None

    from_node = ask_node("Nodo de salida de la fuente: ", nodes)
    to_node = ask_node("Nodo de llegada de la fuente: ", nodes, from_node)

    return {
        "source_id": source_id,
        "source_type": source_type,
        "source_voltage": source_voltage,
        "source_frequency": source_frequency,
        "from_node": from_node,
        "to_node": to_node,
    }


def ask_component(number: int, nodes: list[str], used_ids: set[str]) -> dict[str, object]:
    """Ask for one resistor, capacitor, or inductor."""

    print(f"\n--- Componente {number} ---")
    component_type = ask_choice(
        "Tipo (resistor, capacitor o inductor): ", set(COMPONENT_ID_PREFIXES)
    )
    expected_prefix = COMPONENT_ID_PREFIXES[component_type]

    def check_component_id(value: str) -> str | None:
        if not value.startswith(expected_prefix) or not value[1:].isdigit() or value[1:] == "0":
            return f"Para {component_type}, usa un ID como {expected_prefix}1."
        if value in used_ids:
            return "Ese ID ya se usó."
        return None

    component_id = ask_until_valid("ID del componente: ", check_component_id)
    used_ids.add(component_id)
    component_value = ask_number("Valor: ", True)
    component_prefix = ask_choice(
        "Prefijo (, p, n, u, m, k, M, G o T): ", set(ENGINEERING_PREFIXES)
    )
    expected_unit = COMPONENT_UNITS[component_type]
    component_unit = ask_choice(f"Unidad ({expected_unit}): ", {expected_unit})
    from_node = ask_node("Nodo de salida: ", nodes)
    to_node = ask_node("Nodo de llegada: ", nodes, from_node)

    return {
        "component_id": component_id,
        "component_type": component_type,
        "component_value": component_value,
        "component_prefix": component_prefix,
        "component_unit": component_unit,
        "from_node": from_node,
        "to_node": to_node,
    }


def ask_component_count() -> int:
    """Ask for the number of components to add."""

    def check(value: str) -> str | None:
        if not value.isdigit() or int(value) < 1:
            return "Escribe un entero mayor que cero."
        return None

    return int(ask_until_valid("Cantidad de componentes: ", check))


def collect_circuit_from_user() -> dict[str, object]:
    """Ask for one whole circuit in a simple order."""

    print("\nEscribe los datos. Si algo está mal, te avisará de inmediato.\n")
    circuit_id = ask_non_empty("ID del circuito (ejemplo C001): ")
    circuit_name = ask_non_empty("Nombre del circuito: ")
    circuit_type = ask_choice(
        "Tipo (series, parallel o series-parallel): ", SUPPORTED_CIRCUIT_TYPES
    )
    nodes = ask_nodes()
    source = ask_source(nodes)
    component_count = ask_component_count()
    used_ids: set[str] = set()
    components = [ask_component(number, nodes, used_ids) for number in range(1, component_count + 1)]

    return {
        "circuit_id": circuit_id,
        "circuit_name": circuit_name,
        "circuit_type": circuit_type,
        "source": source,
        "nodes": nodes,
        "components": components,
    }


def run_manual_validation() -> None:
    """Run the manual console flow and show the final result."""

    circuit = collect_circuit_from_user()
    is_valid, errors = validate_circuit(circuit)
    print("\n--- Resultado final ---")
    print(f"Circuito válido: {is_valid}")

    if errors:
        for error in errors:
            print(f"- {error}")
    else:
        print("Todo bien: el circuito pasó todas las validaciones.")


if __name__ == "__main__":
    run_manual_validation()
