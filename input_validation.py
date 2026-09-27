# Funciones básicas para revisar los datos de un circuito.

from __future__ import annotations

import math
import re
from numbers import Real


# Estos son los tipos de circuito que el proyecto entiende por ahora.

SUPPORTED_CIRCUIT_TYPES = {"series", "parallel", "series-parallel"}

# Los nodos se escriben solo con letras mayúsculas, como A, B, AA o AB.

NODE_PATTERN = re.compile(r"^[A-Z]+$")


def is_valid_number(value: object) -> bool:
    """Return whether a value is a finite non-boolean real number."""

    # Dice si un valor sirve como número para el proyecto.

    # Python trata True y False como números, pero para un circuito no queremos
    # que True termine significando 1 ni que False termine significando 0.

    return (
        isinstance(value, Real)
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def validate_nodes(nodes: object) -> list[str]:
    """Return errors found in the circuit node list."""

    # Primero revisamos la lista porque el resto de las reglas necesita nodos
    # para poder tener sentido.

    if not isinstance(nodes, list):
        return ["nodes must be a list."]

    errors: list[str] = []

    # Con menos de dos nodos no hay entre qué puntos conectar un circuito.

    if len(nodes) < 2:
        errors.append("nodes must contain at least two nodes.")

    # Guardamos los nodos ya vistos para saber si alguien escribió uno dos veces.

    seen_nodes: set[str] = set()

    for index, node in enumerate(nodes):
        label = f"nodes[{index}]"

        if not isinstance(node, str):
            errors.append(f"{label} must be a string.")
            continue

        if not NODE_PATTERN.fullmatch(node):
            errors.append(f"{label} must contain uppercase letters only.")

        if node in seen_nodes:
            errors.append(f"{label}: duplicate node identifier {node!r}.")

        seen_nodes.add(node)

    return errors


def validate_circuit(current_circuit: object) -> tuple[bool, list[str]]:
    """Validate the basic circuit fields and nodes."""

    # Revisa el ID, el nombre, el tipo y los nodos, y devuelve los errores.
    # También deja is_valid y error_message listos para que otra parte del
    # programa pueda saber si hay problemas.

    if not isinstance(current_circuit, dict):
        # Si no llega un diccionario, no podemos buscar los datos del circuito.

        return False, ["current_circuit must be a dictionary."]

    # Guardamos todos los errores para mostrarlos juntos, no uno por uno.

    errors: list[str] = []

    # Los dos campos necesitan texto con algo escrito, no espacios vacíos.

    for field in ("circuit_id", "circuit_name"):
        value = current_circuit.get(field)

        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string.")

    # Aquí evitamos que entre un tipo que el programa todavía no conoce.

    if current_circuit.get("circuit_type") not in SUPPORTED_CIRCUIT_TYPES:
        errors.append(
            "circuit_type must be 'series', 'parallel', or 'series-parallel'."
        )

    # La validación de nodos vive aparte para que se pueda probar y entender
    # sin mezclarla con los otros datos del circuito.

    errors.extend(validate_nodes(current_circuit.get("nodes")))

    # Solo cambiamos estas dos claves; las demás partes del circuito todavía
    # se revisarán en los siguientes pasos.

    is_valid = not errors
    current_circuit["is_valid"] = is_valid
    current_circuit["error_message"] = "; ".join(errors)
    return is_valid, errors
