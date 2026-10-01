# Pruebas de las validaciones que el proyecto tiene hasta ahora.

from __future__ import annotations

import math
import unittest

from input_validation import (
    is_valid_number,
    validate_circuit,
    validate_components,
    validate_nodes,
    validate_source,
)


def valid_circuit() -> dict[str, object]:
    """Return the smallest circuit that is valid through Step 4."""

    # Crea el circuito más pequeño que debería pasar las validaciones hasta Step 4.

    return {
        "circuit_id": "C001",
        "circuit_name": "Circuit 1",
        "circuit_type": "series",
        "nodes": ["A", "B", "C"],
        "source": {
            "source_id": "V1",
            "source_type": "DC",
            "source_voltage": 12.0,
            "source_frequency": None,
            "from_node": "A",
            "to_node": "C",
        },
        "components": [
            {
                "component_id": "R1",
                "component_type": "resistor",
                "component_value": 10.0,
                "component_prefix": "k",
                "component_unit": "ohm",
                "from_node": "A",
                "to_node": "B",
            }
        ],
    }


class NumericSafetyTests(unittest.TestCase):
    # Prueba los números que aceptamos o rechazamos.

    def test_finite_integer_and_float_are_valid(self) -> None:
        # Un entero y un decimal normales deben pasar.

        self.assertTrue(is_valid_number(12))
        self.assertTrue(is_valid_number(12.5))

    def test_unsafe_or_non_numeric_values_are_invalid(self) -> None:
        # Estos valores pueden verse como números o venir de un formulario,
        # pero no sirven para los cálculos que el proyecto hará después.

        invalid_values = (True, False, math.nan, math.inf, -math.inf, "12", None)

        for value in invalid_values:
            with self.subTest(value=value):
                self.assertFalse(is_valid_number(value))


class BasicCircuitValidationTests(unittest.TestCase):
    # Prueba solo el ID, el nombre y el tipo de circuito.

    def test_valid_circuit_updates_status_fields(self) -> None:
        # Un circuito correcto debe quedar marcado como válido y sin mensajes.

        circuit = valid_circuit()
        is_valid, errors = validate_circuit(circuit)

        self.assertTrue(is_valid)
        self.assertEqual(errors, [])
        self.assertTrue(circuit["is_valid"])
        self.assertEqual(circuit["error_message"], "")
        self.assertTrue(circuit["has_source"])
        self.assertTrue(circuit["has_components"])

    def test_non_dictionary_circuit_is_invalid(self) -> None:
        # También revisamos que no falle de forma rara si llega una lista.

        is_valid, errors = validate_circuit([])

        self.assertFalse(is_valid)
        self.assertEqual(errors, ["current_circuit must be a dictionary."])

    def test_invalid_circuit_id_is_reported(self) -> None:
        # Probamos ID ausente, vacío y con solo espacios sin copiar la misma
        # prueba tres veces.

        for value in (None, "", "   "):
            with self.subTest(value=value):
                circuit = valid_circuit()
                circuit["circuit_id"] = value
                is_valid, errors = validate_circuit(circuit)

                self.assertFalse(is_valid)
                self.assertTrue(any("circuit_id" in error for error in errors))
                self.assertFalse(circuit["is_valid"])
                self.assertTrue(circuit["error_message"])

    def test_missing_circuit_id_is_reported(self) -> None:
        circuit = valid_circuit()
        circuit.pop("circuit_id")
        is_valid, errors = validate_circuit(circuit)

        self.assertFalse(is_valid)
        self.assertTrue(any("circuit_id" in error for error in errors))

    def test_invalid_circuit_name_is_reported(self) -> None:
        # El nombre sigue las mismas reglas sencillas que el ID.

        for value in (None, "", "   "):
            with self.subTest(value=value):
                circuit = valid_circuit()
                circuit["circuit_name"] = value
                is_valid, errors = validate_circuit(circuit)

                self.assertFalse(is_valid)
                self.assertTrue(any("circuit_name" in error for error in errors))

    def test_missing_circuit_name_is_reported(self) -> None:
        circuit = valid_circuit()
        circuit.pop("circuit_name")
        is_valid, errors = validate_circuit(circuit)

        self.assertFalse(is_valid)
        self.assertTrue(any("circuit_name" in error for error in errors))

    def test_unsupported_circuit_type_is_reported(self) -> None:
        # "mesh" puede sonar válido, pero todavía no está en los tipos acordados.

        circuit = valid_circuit()
        circuit["circuit_type"] = "mesh"
        is_valid, errors = validate_circuit(circuit)

        self.assertFalse(is_valid)
        self.assertTrue(any("circuit_type" in error for error in errors))

    def test_multiple_basic_errors_are_collected(self) -> None:
        # Queremos ver varios errores juntos para no corregir uno, ejecutar y
        # recién descubrir el siguiente.

        circuit = valid_circuit()
        circuit["circuit_id"] = ""
        circuit["circuit_name"] = ""
        circuit["circuit_type"] = "unknown"
        is_valid, errors = validate_circuit(circuit)

        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 3)
        self.assertFalse(circuit["is_valid"])
        self.assertIn("circuit_id", circuit["error_message"])
        self.assertIn("circuit_name", circuit["error_message"])
        self.assertIn("circuit_type", circuit["error_message"])


class NodeValidationTests(unittest.TestCase):
    # Prueba solamente las reglas de nodos agregadas en el Step 2.

    def test_valid_nodes_are_accepted(self) -> None:
        self.assertEqual(validate_nodes(["A", "B", "AA", "AB"]), [])

    def test_nodes_must_be_a_list_with_at_least_two_items(self) -> None:
        cases = ((None, "nodes must be a list"), ("A,B", "nodes must be a list"),
                 ([], "at least two nodes"), (["A"], "at least two nodes"))

        for nodes, text in cases:
            with self.subTest(nodes=nodes):
                self.assertTrue(any(text in error for error in validate_nodes(nodes)))

    def test_node_names_must_be_uppercase_letters(self) -> None:
        invalid_nodes = (["A", "a"], ["A", "A1"], ["A", "NODE_1"], ["A", 2])

        for nodes in invalid_nodes:
            with self.subTest(nodes=nodes):
                self.assertNotEqual(validate_nodes(nodes), [])

    def test_duplicate_nodes_are_rejected(self) -> None:
        errors = validate_nodes(["A", "B", "A"])

        self.assertTrue(any("duplicate node" in error for error in errors))

    def test_validate_circuit_includes_node_errors(self) -> None:
        circuit = valid_circuit()
        circuit["nodes"] = ["A", "A"]
        is_valid, errors = validate_circuit(circuit)

        self.assertFalse(is_valid)
        self.assertTrue(any("duplicate node" in error for error in errors))
        self.assertIn("duplicate node", circuit["error_message"])

    def test_missing_nodes_are_reported_by_validate_circuit(self) -> None:
        circuit = valid_circuit()
        circuit.pop("nodes")
        is_valid, errors = validate_circuit(circuit)

        self.assertFalse(is_valid)
        self.assertTrue(any("nodes must be a list" in error for error in errors))


class SourceValidationTests(unittest.TestCase):
    # Prueba solamente las reglas de fuente agregadas en el Step 3.

    def test_valid_ac_source_is_accepted(self) -> None:
        circuit = valid_circuit()
        circuit["source"].update(source_type="AC", source_frequency=60.0)

        self.assertTrue(validate_circuit(circuit)[0])

    def test_negative_source_voltage_is_accepted(self) -> None:
        circuit = valid_circuit()
        circuit["source"]["source_voltage"] = -12.0

        self.assertTrue(validate_circuit(circuit)[0])
        self.assertTrue(circuit["has_source"])

    def test_source_presence_updates_has_source(self) -> None:
        missing_source = object()
        cases = (
            (missing_source, "source is required"),
            (None, "source is required"),
            ({}, "source is required"),
            ("V1", "source is required"),
        )

        for source, text in cases:
            with self.subTest(source=source):
                circuit = valid_circuit()

                if source is missing_source:
                    circuit.pop("source")
                else:
                    circuit["source"] = source

                is_valid, errors = validate_circuit(circuit)

                self.assertFalse(is_valid)
                self.assertTrue(any(text in error for error in errors))
                self.assertFalse(circuit["has_source"])

    def test_source_id_type_and_voltage_rules(self) -> None:
        cases = (
            ({"source_id": "V2"}, "source_id must be 'V1'"),
            ({"source_type": "ABC"}, "source_type"),
            ({"source_voltage": "12"}, "source_voltage"),
            ({"source_voltage": True}, "source_voltage"),
            ({"source_voltage": math.nan}, "source_voltage"),
            ({"source_voltage": math.inf}, "source_voltage"),
            ({"source_voltage": -math.inf}, "source_voltage"),
        )

        for changes, text in cases:
            with self.subTest(changes=changes):
                circuit = valid_circuit()
                circuit["source"].update(changes)
                self.assertFalse(validate_circuit(circuit)[0])
                self.assertIn(text, circuit["error_message"])

    def test_frequency_rules(self) -> None:
        cases = (
            ({"source_type": "AC", "source_frequency": None}, "source_frequency"),
            ({"source_type": "AC", "source_frequency": 0}, "greater than zero"),
            ({"source_type": "AC", "source_frequency": -60}, "greater than zero"),
            ({"source_type": "AC", "source_frequency": math.nan}, "source_frequency"),
            ({"source_type": "AC", "source_frequency": math.inf}, "source_frequency"),
            ({"source_type": "AC", "source_frequency": True}, "source_frequency"),
            ({"source_type": "DC", "source_frequency": 60}, "must be None"),
        )

        for changes, text in cases:
            with self.subTest(changes=changes):
                circuit = valid_circuit()
                circuit["source"].update(changes)
                self.assertFalse(validate_circuit(circuit)[0])
                self.assertIn(text, circuit["error_message"])

    def test_ac_source_with_missing_frequency_is_invalid(self) -> None:
        circuit = valid_circuit()
        circuit["source"].update(source_type="AC")
        circuit["source"].pop("source_frequency")
        is_valid, errors = validate_circuit(circuit)

        self.assertFalse(is_valid)
        self.assertTrue(any("source_frequency" in error for error in errors))

    def test_source_connections_must_use_two_existing_nodes(self) -> None:
        cases = (
            ({"from_node": "Z"}, "not in nodes"),
            ({"to_node": "Z"}, "not in nodes"),
            ({"to_node": "A"}, "must be different"),
        )

        for changes, text in cases:
            with self.subTest(changes=changes):
                circuit = valid_circuit()
                circuit["source"].update(changes)
                self.assertFalse(validate_circuit(circuit)[0])
                self.assertIn(text, circuit["error_message"])

    def test_validate_source_rejects_non_dictionary(self) -> None:
        errors = validate_source(None, ["A", "B"])

        self.assertEqual(errors, ["source must be a dictionary."])


class ComponentValidationTests(unittest.TestCase):
    # Prueba solamente las reglas de componentes agregadas en el Step 4.

    def test_multiple_valid_components_are_accepted(self) -> None:
        circuit = valid_circuit()
        circuit["components"].extend([
            {
                "component_id": "C1",
                "component_type": "capacitor",
                "component_value": 2.0,
                "component_prefix": "u",
                "component_unit": "farad",
                "from_node": "B",
                "to_node": "C",
            },
            {
                "component_id": "L1",
                "component_type": "inductor",
                "component_value": 3.0,
                "component_prefix": "m",
                "component_unit": "henry",
                "from_node": "C",
                "to_node": "A",
            },
        ])

        self.assertTrue(validate_circuit(circuit)[0])
        self.assertTrue(circuit["has_components"])

    def test_component_presence_updates_has_components(self) -> None:
        missing_components = object()
        cases = (
            (missing_components, "components must be a list"),
            (None, "components must be a list"),
            ({}, "components must be a list"),
            ([], "at least one component"),
        )

        for components, text in cases:
            with self.subTest(components=components):
                circuit = valid_circuit()

                if components is missing_components:
                    circuit.pop("components")
                else:
                    circuit["components"] = components

                self.assertFalse(validate_circuit(circuit)[0])
                self.assertIn(text, circuit["error_message"])
                self.assertFalse(circuit["has_components"])

    def test_component_type_ids_and_duplicates(self) -> None:
        cases = (
            ({"component_type": "diode"}, "unsupported component_type"),
            ({"component_id": "X1"}, "component_id"),
            ({"component_id": "C1"}, "component_id"),
        )

        for changes, text in cases:
            with self.subTest(changes=changes):
                circuit = valid_circuit()
                circuit["components"][0].update(changes)
                self.assertFalse(validate_circuit(circuit)[0])
                self.assertIn(text, circuit["error_message"])

        circuit = valid_circuit()
        circuit["components"].append(circuit["components"][0].copy())
        self.assertFalse(validate_circuit(circuit)[0])
        self.assertIn("duplicate component_id", circuit["error_message"])

    def test_component_values_must_be_positive_finite_numbers(self) -> None:
        component_data = {
            "resistor": ("R1", "ohm"),
            "capacitor": ("C1", "farad"),
            "inductor": ("L1", "henry"),
        }

        for component_type, (component_id, unit) in component_data.items():
            for value in (0, -1):
                with self.subTest(component_type=component_type, value=value):
                    circuit = valid_circuit()
                    circuit["components"][0].update(
                        component_id=component_id,
                        component_type=component_type,
                        component_unit=unit,
                        component_value=value,
                    )
                    self.assertFalse(validate_circuit(circuit)[0])
                    self.assertIn("greater than zero", circuit["error_message"])

        for value in (math.nan, math.inf, -math.inf, True, "10"):
            with self.subTest(value=value):
                circuit = valid_circuit()
                circuit["components"][0]["component_value"] = value
                self.assertFalse(validate_circuit(circuit)[0])
                self.assertIn("finite number", circuit["error_message"])

    def test_prefix_unit_and_connections_are_checked(self) -> None:
        cases = (
            ({"component_prefix": "x"}, "component_prefix"),
            ({"component_unit": "farad"}, "component_unit"),
            ({"from_node": "Z"}, "not in nodes"),
            ({"to_node": "Z"}, "not in nodes"),
            ({"to_node": "A"}, "must be different"),
        )

        for changes, text in cases:
            with self.subTest(changes=changes):
                circuit = valid_circuit()
                circuit["components"][0].update(changes)
                self.assertFalse(validate_circuit(circuit)[0])
                self.assertIn(text, circuit["error_message"])

    def test_validate_components_rejects_non_list(self) -> None:
        self.assertEqual(
            validate_components(None, ["A", "B"]),
            ["components must be a list."],
        )

    def test_component_item_must_be_a_dictionary(self) -> None:
        circuit = valid_circuit()
        circuit["components"] = ["R1"]
        is_valid, errors = validate_circuit(circuit)

        self.assertFalse(is_valid)
        self.assertTrue(any("must be a dictionary" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
