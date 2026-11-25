# Funciones básicas para revisar los datos de un circuito.

from __future__ import annotations

import math
import re
from numbers import Real


# Estos son los tipos de circuito que el proyecto entiende por ahora.

SUPPORTED_CIRCUIT_TYPES = {"series", "parallel", "series-parallel"}

# Por ahora trabajamos con una sola fuente de voltaje, llamada V1.

SOURCE_ID = "V1"
SUPPORTED_SOURCE_TYPES = {"AC", "DC"}

# Estas tablas indican qué letra y unidad debe usar cada tipo de componente.

COMPONENT_ID_PREFIXES = {
    "resistor": "R",
    "capacitor": "C",
    "inductor": "L",
}
COMPONENT_UNITS = {
    "resistor": "ohm",
    "capacitor": "farad",
    "inductor": "henry",
}

# El prefijo se guarda separado del valor para convertirlo más adelante.

ENGINEERING_PREFIXES = {"", "p", "n", "u", "m", "k", "M", "G", "T"}

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


def validate_source(source: object, nodes: object) -> list[str]:
    """Return errors found in the circuit voltage source."""

    # La fuente se revisa aparte para que sus reglas no queden mezcladas con
    # las reglas generales del circuito.

    if not isinstance(source, dict):
        return ["source must be a dictionary."]

    errors: list[str] = []
    source_id = source.get("source_id")

    if source_id != SOURCE_ID:
        errors.append("source_id must be 'V1'.")

    # El nombre se usa en los errores para que sea más fácil saber qué dato falló.

    label = source_id if isinstance(source_id, str) else "source"
    source_type = source.get("source_type")

    if source_type not in SUPPORTED_SOURCE_TYPES:
        errors.append(f"{label}: source_type must be 'AC' or 'DC'.")

    if not is_valid_number(source.get("source_voltage")):
        errors.append(f"{label}: source_voltage must be a finite number.")

    frequency = source.get("source_frequency")

    # AC necesita una frecuencia positiva. En DC debe quedar como None.

    if source_type == "AC":
        if not is_valid_number(frequency):
            errors.append(f"{label}: AC source_frequency must be a finite number.")
        elif frequency <= 0:
            errors.append(f"{label}: AC source_frequency must be greater than zero.")
    elif source_type == "DC" and frequency is not None:
        errors.append(f"{label}: DC source_frequency must be None.")

    node_set: set[str] = (
        {node for node in nodes if isinstance(node, str)}
        if isinstance(nodes, list)
        else set()
    )
    from_node = source.get("from_node")
    to_node = source.get("to_node")

    for field, node in (("from_node", from_node), ("to_node", to_node)):
        if not isinstance(node, str):
            errors.append(f"{label}: {field} must be a string.")
        elif node not in node_set:
            errors.append(f"{label}: {field} {node!r} is not in nodes.")

    # Una fuente necesita dos terminales diferentes para tener una conexión útil.

    if isinstance(from_node, str) and from_node == to_node:
        errors.append(f"{label}: from_node and to_node must be different.")

    return errors


def validate_components(components: object, nodes: object) -> list[str]:
    """Return errors found in the circuit component list."""

    if not isinstance(components, list):
        return ["components must be a list."]

    if not components:
        return ["components must contain at least one component."]

    errors: list[str] = []
    component_ids: set[str] = set()
    node_set: set[str] = (
        {node for node in nodes if isinstance(node, str)}
        if isinstance(nodes, list)
        else set()
    )

    for index, component in enumerate(components):
        if not isinstance(component, dict):
            errors.append(f"components[{index}] must be a dictionary.")
            continue

        component_id = component.get("component_id")
        label = (
            component_id
            if isinstance(component_id, str)
            else f"components[{index}]"
        )
        component_type = component.get("component_type")
        expected_prefix = COMPONENT_ID_PREFIXES.get(component_type)

        # El ID cambia según el tipo: R1 es resistor, C1 capacitor y L1 inductor.

        if expected_prefix is None:
            errors.append(f"{label}: unsupported component_type {component_type!r}.")
        elif not isinstance(component_id, str) or not re.fullmatch(
            rf"{expected_prefix}[1-9][0-9]*",
            component_id,
        ):
            errors.append(
                f"{label}: component_id must match {expected_prefix}<number>."
            )

        if isinstance(component_id, str):
            if component_id in component_ids:
                errors.append(f"{component_id}: duplicate component_id.")
            component_ids.add(component_id)

        value = component.get("component_value")

        # Para este proyecto, los componentes pasivos deben tener valor positivo.

        if not is_valid_number(value):
            errors.append(f"{label}: component_value must be a finite number.")
        elif value <= 0:
            errors.append(f"{label}: component_value must be greater than zero.")

        prefix = component.get("component_prefix")

        if not isinstance(prefix, str) or prefix not in ENGINEERING_PREFIXES:
            errors.append(
                f"{label}: component_prefix must be a supported engineering prefix."
            )

        expected_unit = COMPONENT_UNITS.get(component_type)

        if expected_unit is None:
            errors.append(
                f"{label}: component_unit cannot be checked without a valid type."
            )
        elif component.get("component_unit") != expected_unit:
            errors.append(f"{label}: component_unit must be {expected_unit!r}.")

        from_node = component.get("from_node")
        to_node = component.get("to_node")

        for field, node in (("from_node", from_node), ("to_node", to_node)):
            if not isinstance(node, str):
                errors.append(f"{label}: {field} must be a string.")
            elif node not in node_set:
                errors.append(f"{label}: {field} {node!r} is not in nodes.")

        # Un componente necesita dos nodos distintos para quedar conectado.

        if isinstance(from_node, str) and from_node == to_node:
            errors.append(f"{label}: from_node and to_node must be different.")

    return errors


def validate_circuit(current_circuit: object) -> tuple[bool, list[str]]:
    """Validate basic fields, nodes, the voltage source, and components."""

    # Revisa el ID, el nombre, el tipo, los nodos, la fuente y los componentes.
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

    source = current_circuit.get("source")

    # Una fuente vacía no cuenta como fuente presente.

    current_circuit["has_source"] = isinstance(source, dict) and bool(source)

    if not current_circuit["has_source"]:
        errors.append("source is required.")
    else:
        errors.extend(validate_source(source, current_circuit.get("nodes")))

    components = current_circuit.get("components")

    # Una lista vacía tampoco cuenta como tener componentes.

    current_circuit["has_components"] = (
        isinstance(components, list) and bool(components)
    )

    # validate_components ya revisa si falta la lista o si está vacía.

    errors.extend(validate_components(components, current_circuit.get("nodes")))

    is_valid = not errors
    current_circuit["is_valid"] = is_valid
    current_circuit["error_message"] = "; ".join(errors)
    return is_valid, errors
