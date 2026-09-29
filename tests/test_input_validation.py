# Pruebas de las validaciones que el proyecto tiene hasta ahora.

from __future__ import annotations

import math
import unittest

from input_validation import (
    is_valid_number,
    validate_circuit,
    validate_nodes,
    validate_source,
)


def valid_circuit() -> dict[str, object]:
    """Return the smallest circuit that is valid through Step 3."""

    # Crea el circuito más pequeño que debería pasar las validaciones hasta Step 3.

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
        self.assertNotIn("has_components", circuit)

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


if __name__ == "__main__":
    unittest.main()
