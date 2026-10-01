# Programa de consola para probar manualmente la validación de circuitos.

from __future__ import annotations

from input_validation import validate_circuit


# Este archivo no resuelve ni guarda el circuito. Solo arma el diccionario que
# usa el proyecto y se lo pasa al validador para mostrar sus errores.


def read_number(prompt: str) -> object:
    # Convierte a float cuando puede; si no, deja el texto para el validador.

    value = input(prompt)

    try:
        return float(value)
    except ValueError:
        # Dejamos el texto para que validate_circuit dé el mismo mensaje que
        # tendría la futura interfaz.

        return value


def read_frequency() -> object | None:
    # Si la frecuencia se deja vacía, devuelve None para las fuentes DC.

    value = input("Frecuencia (dejar vacío para DC): ")

    if not value.strip():
        return None

    try:
        return float(value)
    except ValueError:
        return value


def read_components() -> list[dict[str, object]]:
    # Pide los datos de cada componente y los guarda en una lista.

    while True:
        raw_count = input("Cantidad de componentes: ")

        try:
            component_count = int(raw_count)
        except ValueError:
            print("Escribe una cantidad entera, por ejemplo 1 o 2.\n")
            continue

        if component_count < 0:
            print("La cantidad no puede ser negativa.\n")
            continue

        break

    components: list[dict[str, object]] = []

    for number in range(1, component_count + 1):
        print(f"\n--- Componente {number} ---")
        components.append(
            {
                "component_id": input("ID (ejemplo R1): "),
                "component_type": input(
                    "Tipo (resistor, capacitor o inductor): "
                ),
                "component_value": read_number("Valor: "),
                "component_prefix": input("Prefijo (, p, n, u, m, k, M, G o T): "),
                "component_unit": input("Unidad (ohm, farad o henry): "),
                "from_node": input("Nodo de salida: "),
                "to_node": input("Nodo de llegada: "),
            }
        )

    return components


def collect_circuit_from_user() -> dict[str, object]:
    # Pide todos los datos y arma el diccionario que usa el proyecto.

    print(
        "\nEscribe los datos del circuito. Al final verás todos los errores juntos.\n"
    )
    nodes = [node.strip() for node in input("Nodos separados por comas: ").split(",")]

    print("\n--- Fuente de voltaje ---")
    source = {
        "source_id": input("ID de la fuente (V1): "),
        "source_type": input("Tipo de fuente (AC o DC): "),
        "source_voltage": read_number("Voltaje: "),
        "source_frequency": read_frequency(),
        "from_node": input("Nodo de salida de la fuente: "),
        "to_node": input("Nodo de llegada de la fuente: "),
    }

    return {
        "circuit_id": input("\nID del circuito (ejemplo C001): "),
        "circuit_name": input("Nombre del circuito: "),
        "circuit_type": input("Tipo (series, parallel o series-parallel): "),
        "nodes": nodes,
        "source": source,
        "components": read_components(),
    }


def show_validation_result(circuit: dict[str, object]) -> None:
    # Muestra si el circuito pasó o los errores que se encontraron.

    is_valid, errors = validate_circuit(circuit)
    print("\n--- Resultado de validación ---")
    print(f"Circuito válido: {is_valid}")

    if errors:
        print("Errores encontrados:")

        for error in errors:
            print(f"- {error}")
    else:
        print("Todo bien: el circuito pasó las validaciones.")


def main() -> None:
    # Ejecuta el flujo manual completo.

    circuit = collect_circuit_from_user()
    show_validation_result(circuit)


if __name__ == "__main__":
    main()
