"""Input validation for Circuit Generator circuit dictionaries."""

from __future__ import annotations

import math
import re
from numbers import Real
from typing import Any

# ---------------------------------------------------------------------------
# Reglas compartidas por todo el modulo
# ---------------------------------------------------------------------------
#
# Estas son las opciones que el programa entiende. Si agregamos algo nuevo,
# lo ponemos aqui para no tener que cambiar varias partes del archivo.
#
# Estos son los tipos de circuito que usamos por ahora.

SUPPORTED_CIRCUIT_TYPES = {"series", "parallel", "series-parallel"}

# Aqui dice que letra y unidad le toca a cada componente.

COMPONENT_ID_PREFIXES = {"resistor": "R", "capacitor": "C", "inductor": "L"}
COMPONENT_UNITS = {"resistor": "ohm", "capacitor": "farad", "inductor": "henry"}

# Estos son los prefijos que se pueden escribir, como k o m.

ENGINEERING_PREFIXES = {
    "": 1.0, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3,
    "k": 1e3, "M": 1e6, "G": 1e9, "T": 1e12,
}

# Los nodos pueden ser A, AA o AB. Solo usamos letras mayusculas.

NODE_PATTERN = re.compile(r"^[A-Z]+$")

# Por ahora el proyecto usa una sola fuente, siempre llamada V1.


def is_valid_number(value: object) -> bool:
    """Return whether value is a finite real number, excluding booleans."""

    # True parece un numero para Python, pero aqui no queremos aceptarlo.
    # Tampoco queremos aceptar NaN o infinito.

    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)


# ---------------------------------------------------------------------------
# Validacion de nodos y conexiones
# ---------------------------------------------------------------------------
#
# Primero revisamos los nodos. Despues usamos esa lista para ver que las
# conexiones no apunten a un nodo que no existe.
#

def validate_nodes(nodes: object) -> list[str]:
    """Validate node storage, identifiers, and duplicates."""
    if not isinstance(nodes, list):
        return ["nodes must be a list."]
    errors: list[str] = []

    # Necesitamos por lo menos dos nodos para poder conectar algo.

    if len(nodes) < 2:
        errors.append("nodes must contain at least two nodes.")

    # Este set nos ayuda a ver si un nodo se repite.

    seen: set[str] = set()
    for index, node in enumerate(nodes):
        label = f"nodes[{index}]"
        if not isinstance(node, str):
            errors.append(f"{label} must be a string.")
        else:
            if not NODE_PATTERN.fullmatch(node):
                errors.append(f"{label} must be an uppercase node identifier.")
            if node in seen:
                errors.append(f"{label}: duplicate node identifier {node!r}.")
            seen.add(node)
    return errors


def _validate_connection(
    item: dict[str, Any], label: str, node_set: set[str], errors: list[str]
) -> None:
    """Add endpoint errors for a source or component to ``errors``.

    ``item`` is deliberately received as a dictionary only after its caller
    verified that structure. ``label`` makes every error identify its source,
    for example ``R1`` instead of a generic and less useful message.
    """
    # Los dos extremos tienen que estar en la lista de nodos.
    from_node, to_node = item.get("from_node"), item.get("to_node")
    for field, node in (("from_node", from_node), ("to_node", to_node)):
        if not isinstance(node, str):
            errors.append(f"{label}: {field} must be a string.")
        elif node not in node_set:
            errors.append(f"{label}: {field} {node!r} is not in nodes.")

    # No dejamos conectar algo del nodo A al mismo nodo A.
    
    if isinstance(from_node, str) and from_node == to_node:
        errors.append(f"{label}: from_node and to_node must be different.")


# ---------------------------------------------------------------------------
# Validacion de fuente de voltaje
# ---------------------------------------------------------------------------
#
# Aqui solo vemos que los datos de la fuente tengan sentido. Todavia no
# intentamos calcular el circuito.
#
def _validate_source(source: dict[str, Any], node_set: set[str]) -> list[str]:
    """Return every input error found in one source dictionary."""
    errors: list[str] = []
    # Aunque el ID este mal, seguimos para mostrar los otros errores tambien.
    source_id = source.get("source_id")
    if source_id != "V1":
        errors.append("source_id must be 'V1'.")
    label = source_id if isinstance(source_id, str) else "source"
    # AC necesita frecuencia; DC la deja vacia.
    source_type = source.get("source_type")
    if source_type not in {"AC", "DC"}:
        errors.append(f"{label}: source_type must be 'AC' or 'DC'.")
    # El voltaje puede ser negativo, pero no texto, True, NaN ni infinito.
    if not is_valid_number(source.get("source_voltage")):
        errors.append(f"{label}: source_voltage must be a finite number.")
    frequency = source.get("source_frequency")
    if source_type == "AC":
        if not is_valid_number(frequency):
            errors.append(f"{label}: AC source_frequency must be a finite number.")
        elif frequency <= 0:
            errors.append(f"{label}: AC source_frequency must be greater than zero.")
    elif source_type == "DC" and frequency is not None:
        errors.append(f"{label}: DC source_frequency must be None.")
    _validate_connection(source, label, node_set, errors)
    return errors


# ---------------------------------------------------------------------------
# Validacion de componentes pasivos
# ---------------------------------------------------------------------------
#
# Resistores, capacitores e inductores se parecen mucho, asi que los revisamos
# juntos. Las tablas de arriba dicen que letra y unidad usa cada uno.
#
def _validate_component(
    component: object, index: int, node_set: set[str]
) -> tuple[list[str], str | None]:
    """Return component errors and its string ID, when one was supplied.

    The returned ID lets ``validate_circuit`` check duplicate identifiers in
    the complete component list. Keeping that check outside this function is
    necessary because a component does not know about its siblings.
    """
    if not isinstance(component, dict):
        return [f"components[{index}] must be a dictionary."], None
    errors: list[str] = []
    component_id = component.get("component_id")
    label = component_id if isinstance(component_id, str) else f"components[{index}]"
    component_type = component.get("component_type")
    # La letra del ID tiene que ir con el tipo: R1 es resistor, C1 es capacitor.
    expected_prefix = COMPONENT_ID_PREFIXES.get(component_type)
    if expected_prefix is None:
        errors.append(f"{label}: unsupported component_type {component_type!r}.")
    elif not isinstance(component_id, str) or not re.fullmatch(
        rf"{expected_prefix}[1-9][0-9]*", component_id
    ):
        errors.append(f"{label}: component_id must match {expected_prefix}<number>.")
    # Para este proyecto, estos valores no pueden ser cero ni negativos.
    value = component.get("component_value")
    if not is_valid_number(value):
        errors.append(f"{label}: component_value must be a finite number.")
    elif value <= 0:
        errors.append(f"{label}: component_value must be greater than zero.")
    # Aqui solo vemos si el prefijo existe. La conversion viene despues.
    prefix = component.get("component_prefix")
    if not isinstance(prefix, str) or prefix not in ENGINEERING_PREFIXES:
        errors.append(f"{label}: component_prefix must be a supported engineering prefix.")
    # Revisamos que la unidad vaya con el componente.
    expected_unit = COMPONENT_UNITS.get(component_type)
    if component.get("component_unit") != expected_unit:
        if expected_unit is None:
            errors.append(f"{label}: component_unit cannot be validated without a valid type.")
        else:
            errors.append(f"{label}: component_unit must be {expected_unit!r}.")
    _validate_connection(component, label, node_set, errors)
    return errors, component_id if isinstance(component_id, str) else None


# ---------------------------------------------------------------------------
# Punto de entrada publico
# ---------------------------------------------------------------------------
#
# Esta es la funcion principal. Revisa todo y junta los errores para que se
# puedan arreglar varios de una vez.
#
def validate_circuit(current_circuit: object) -> tuple[bool, list[str]]:
    """Validate a circuit dictionary and update its validation status fields.

    Args:
        current_circuit: Untrusted data expected to follow the shared circuit
            dictionary structure. It is typed as ``object`` because checking
            its type is part of this function's job.

    Returns:
        A pair ``(is_valid, errors)``. ``errors`` contains every independent
        problem found, and is empty only when ``is_valid`` is ``True``.

    Side effects:
        For a dictionary input, only ``is_valid``, ``error_message``,
        ``has_source``, and ``has_components`` are written or updated. The
        circuit definition, including user values and connections, is not
        changed by this validation process.
    """
    if not isinstance(current_circuit, dict):
        # Si no es un diccionario, no hay nada que revisar.
        return False, ["current_circuit must be a dictionary."]
    # Guardamos los errores en una lista.
    errors: list[str] = []
    # Usamos strip solo para ver si escribieron algo; no cambiamos su texto.
    for field in ("circuit_id", "circuit_name"):
        value = current_circuit.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string.")
    # Si llega otro tipo, avisamos antes de seguir.
    if current_circuit.get("circuit_type") not in SUPPORTED_CIRCUIT_TYPES:
        errors.append("circuit_type must be 'series', 'parallel', or 'series-parallel'.")
    # Revisamos los nodos antes de revisar las conexiones.
    nodes = current_circuit.get("nodes")
    errors.extend(validate_nodes(nodes))
    # Guardamos los nodos en un set para buscarlos facil.
    node_set = {node for node in nodes if isinstance(node, str)} if isinstance(nodes, list) else set()

    # Estas banderas salen de los datos actuales, no de lo que habia antes.
    source = current_circuit.get("source")
    current_circuit["has_source"] = isinstance(source, dict) and bool(source)
    if not current_circuit["has_source"]:
        errors.append("source is required.")
    else:
        errors.extend(_validate_source(source, node_set))

    components = current_circuit.get("components")
    # Una lista vacia cuenta como no tener componentes.
    current_circuit["has_components"] = isinstance(components, list) and bool(components)
    if not isinstance(components, list):
        errors.append("components must be a list.")
    elif not components:
        errors.append("components must contain at least one component.")
    else:
        # Aqui guardamos los IDs que ya aparecieron.
        component_ids: set[str] = set()
        for index, component in enumerate(components):
            component_errors, component_id = _validate_component(component, index, node_set)
            errors.extend(component_errors)
            # Igual avisamos si el ID se repite, aunque tenga otro error.
            if component_id is not None:
                if component_id in component_ids:
                    errors.append(f"{component_id}: duplicate component_id.")
                component_ids.add(component_id)
    # Solo cambiamos estas cuatro claves; lo demas queda igual.
    is_valid = not errors
    current_circuit["is_valid"] = is_valid
    current_circuit["error_message"] = "; ".join(errors)
    return is_valid, errors
