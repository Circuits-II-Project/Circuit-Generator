"""Automated checks for the circuit input validator."""

from __future__ import annotations

import copy
import math
import unittest

from input_validation import validate_circuit


def valid_circuit() -> dict[str, object]:
    """Return a fresh circuit that should pass every validation rule."""

    return {
        "circuit_id": "C001",
        "circuit_name": "Circuit 1",
        "circuit_type": "series",
        "source": {
            "source_id": "V1",
            "source_type": "DC",
            "source_voltage": 12.0,
            "source_frequency": None,
            "from_node": "A",
            "to_node": "C",
        },
        "nodes": ["A", "B", "C"],
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


class ValidateCircuitTests(unittest.TestCase):
    """Check valid circuits, bad fields, and the status fields we update."""

    def assert_invalid(self, circuit: object, expected_text: str) -> None:
        """Check that validation fails and mentions the expected problem."""

        is_valid, errors = validate_circuit(circuit)
        self.assertFalse(is_valid)
        self.assertTrue(any(expected_text in error for error in errors), errors)

    def test_valid_dc_circuit_updates_status_fields(self) -> None:
        circuit = valid_circuit()
        is_valid, errors = validate_circuit(circuit)

        self.assertTrue(is_valid)
        self.assertEqual(errors, [])
        self.assertTrue(circuit["is_valid"])
        self.assertEqual(circuit["error_message"], "")
        self.assertTrue(circuit["has_source"])
        self.assertTrue(circuit["has_components"])

    def test_valid_ac_and_multiple_components(self) -> None:
        circuit = valid_circuit()
        circuit["source"].update(source_type="AC", source_frequency=60.0)
        circuit["components"].extend([
            {"component_id": "C1", "component_type": "capacitor", "component_value": 2.0,
             "component_prefix": "u", "component_unit": "farad", "from_node": "B", "to_node": "C"},
            {"component_id": "L1", "component_type": "inductor", "component_value": 3.0,
             "component_prefix": "m", "component_unit": "henry", "from_node": "C", "to_node": "A"},
        ])

        self.assertTrue(validate_circuit(circuit)[0])

    def test_general_fields(self) -> None:
        cases = (
            ("circuit_id", "", "circuit_id"),
            ("circuit_name", "   ", "circuit_name"),
            ("circuit_type", "mesh", "circuit_type"),
            ("nodes", "A,B", "nodes must be a list"),
            ("components", {}, "components must be a list"),
        )
        for field, value, text in cases:
            with self.subTest(field=field):
                circuit = valid_circuit()
                circuit[field] = value
                self.assert_invalid(circuit, text)

    def test_node_rules(self) -> None:
        for nodes, text in ((["A", "A"], "duplicate node"),
                            (["A", "node_1"], "uppercase"),
                            (["A", "A1"], "uppercase"),
                            (["A"], "at least two")):
            with self.subTest(nodes=nodes):
                circuit = valid_circuit()
                circuit["nodes"] = nodes
                self.assert_invalid(circuit, text)

    def test_source_presence_and_status_fields(self) -> None:
        for source, text in ((None, "source is required"), ({}, "source is required")):
            with self.subTest(source=source):
                circuit = valid_circuit()
                circuit["source"] = source
                self.assert_invalid(circuit, text)
                self.assertFalse(circuit["has_source"])
                self.assertFalse(circuit["is_valid"])
                self.assertTrue(circuit["error_message"])

        circuit = valid_circuit()
        circuit["components"] = []
        self.assert_invalid(circuit, "at least one component")
        self.assertFalse(circuit["has_components"])

    def test_source_fields_and_connections(self) -> None:
        cases = (
            ({"source_id": "V2"}, "source_id must be 'V1'"),
            ({"source_type": "ABC"}, "source_type"),
            ({"source_type": "AC", "source_frequency": None}, "source_frequency"),
            ({"source_type": "AC", "source_frequency": 0}, "greater than zero"),
            ({"source_type": "DC", "source_frequency": 60}, "must be None"),
            ({"to_node": "Z"}, "not in nodes"),
            ({"to_node": "A"}, "must be different"),
        )
        for changes, text in cases:
            with self.subTest(changes=changes):
                circuit = valid_circuit()
                circuit["source"].update(changes)
                self.assert_invalid(circuit, text)

    def test_component_identity_and_connections(self) -> None:
        cases = (
            ({"component_type": "diode"}, "unsupported"),
            ({"component_id": "X1"}, "component_id"),
            ({"component_id": "C1"}, "component_id"),
            ({"to_node": "Z"}, "not in nodes"),
            ({"to_node": "A"}, "must be different"),
            ({"component_prefix": "x"}, "component_prefix"),
            ({"component_unit": "farad"}, "component_unit"),
        )
        for changes, text in cases:
            with self.subTest(changes=changes):
                circuit = valid_circuit()
                circuit["components"][0].update(changes)
                self.assert_invalid(circuit, text)

        circuit = valid_circuit()
        circuit["components"].append(copy.deepcopy(circuit["components"][0]))
        self.assert_invalid(circuit, "duplicate component_id")

    def test_component_values_must_be_positive(self) -> None:
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
                    self.assert_invalid(circuit, "greater than zero")

    def test_unsafe_numeric_values(self) -> None:
        for value in (math.nan, math.inf, -math.inf, True):
            with self.subTest(value=value):
                circuit = valid_circuit()
                circuit["components"][0]["component_value"] = value
                self.assert_invalid(circuit, "finite number")

    def test_non_dictionary_circuit(self) -> None:
        is_valid, errors = validate_circuit([])
        self.assertFalse(is_valid)
        self.assertEqual(errors, ["current_circuit must be a dictionary."])


if __name__ == "__main__":
    unittest.main()
