# Funciones básicas para revisar los datos de un circuito.

from __future__ import annotations

import math
from numbers import Real


# Estos son los tipos de circuito que el proyecto entiende por ahora.

SUPPORTED_CIRCUIT_TYPES = {"series", "parallel", "series-parallel"}


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


def validate_circuit(current_circuit: object) -> tuple[bool, list[str]]:
    """Validate the Step 1 fields and return ``(is_valid, errors)``."""

    # Revisa el ID, el nombre y el tipo de circuito, y devuelve los errores.
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

    # Solo cambiamos estas dos claves; las demás partes del circuito todavía
    # se revisarán en los siguientes pasos.

    is_valid = not errors
    current_circuit["is_valid"] = is_valid
    current_circuit["error_message"] = "; ".join(errors)
    return is_valid, errors
