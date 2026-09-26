# Pruebas pequeñas para el primer paso de validación.

from __future__ import annotations

import math
import unittest

from input_validation import is_valid_number, validate_circuit


def valid_circuit() -> dict[str, object]:
    """Return the smallest circuit that is valid in Step 1."""

    # Crea el circuito más pequeño que debería pasar este primer paso.

    return {
        "circuit_id": "C001",
        "circuit_name": "Circuit 1",
        "circuit_type": "series",
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
        self.assertNotIn("has_source", circuit)
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

        circuit = {"circuit_id": "", "circuit_type": "unknown"}
        is_valid, errors = validate_circuit(circuit)

        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 3)
        self.assertFalse(circuit["is_valid"])
        self.assertIn("circuit_id", circuit["error_message"])
        self.assertIn("circuit_name", circuit["error_message"])
        self.assertIn("circuit_type", circuit["error_message"])


if __name__ == "__main__":
    unittest.main()
