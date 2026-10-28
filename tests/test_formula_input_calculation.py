import math
import unittest

from formula_service import calculate_formula


# Cada caso comprueba que la opción llegue a la fórmula correcta y use su resultado.
class FormulaInputCalculationTests(unittest.TestCase):
    def test_dc_basic_formula_routes(self) -> None:
        cases = (
            ("1", {"current": 0.005, "resistance": 100.0}, "resistor_voltage", 0.5),
            ("2", {"voltage": 10.0, "resistance": 5.0}, "resistor_current", 2.0),
            ("3", {"current": 2.0, "voltage": 3.0}, "resistor_power", 6.0),
            ("4", {"resistances": [10.0, 20.0]}, "equivalent_resistance", 30.0),
            ("5", {"resistances": [10.0, 20.0]}, "equivalent_resistance", 20 / 3),
        )

        for option, values, key, expected in cases:
            with self.subTest(option=option):
                result = calculate_formula(option, values)
                self.assertEqual(set(result), {key})
                self.assertAlmostEqual(result[key], expected)

    def test_inductor_formula_routes(self) -> None:
        cases = (
            (
                "6",
                {
                    "inductance": 2.0,
                    "previous_current": 1.0,
                    "current": 4.0,
                    "previous_time": 0.0,
                    "time": 3.0,
                },
                "inductor_voltage",
                2.0,
            ),
            ("7", {"inductances": [2.0, 3.0]}, "equivalent_inductance", 5.0),
            ("8", {"inductances": [2.0, 3.0]}, "equivalent_inductance", 1.2),
            (
                "9",
                {
                    "inductance": 2.0,
                    "previous_current": 1.0,
                    "instant_current": 4.0,
                    "previous_time": 0.0,
                    "time": 3.0,
                },
                "inductor_power",
                8.0,
            ),
        )

        for option, values, key, expected in cases:
            with self.subTest(option=option):
                result = calculate_formula(option, values)
                self.assertEqual(set(result), {key})
                self.assertAlmostEqual(result[key], expected)

    def test_capacitor_formula_routes(self) -> None:
        cases = (
            (
                "10",
                {
                    "capacitance": 2.0,
                    "previous_voltage": 1.0,
                    "voltage": 4.0,
                    "previous_time": 0.0,
                    "time": 3.0,
                },
                "capacitor_current",
                2.0,
            ),
            ("11", {"capacitances": [2.0, 3.0]}, "equivalent_capacitance", 1.2),
            ("12", {"capacitances": [2.0, 3.0]}, "equivalent_capacitance", 5.0),
            (
                "13",
                {
                    "capacitance": 2.0,
                    "previous_voltage": 1.0,
                    "instant_voltage": 4.0,
                    "previous_time": 0.0,
                    "time": 3.0,
                },
                "capacitor_power",
                8.0,
            ),
        )

        for option, values, key, expected in cases:
            with self.subTest(option=option):
                result = calculate_formula(option, values)
                self.assertEqual(set(result), {key})
                self.assertAlmostEqual(result[key], expected)

    def test_ac_formula_routes(self) -> None:
        polar_result = calculate_formula("14", {"real": 3.0, "imaginary": 4.0})
        self.assertEqual(set(polar_result), {"magnitude", "angle_degrees"})
        self.assertAlmostEqual(polar_result["magnitude"], 5.0)
        self.assertAlmostEqual(polar_result["angle_degrees"], 53.13010235415598)

        rectangular_result = calculate_formula(
            "15",
            {"magnitude": 5.0, "angle_degrees": 90.0},
        )
        self.assertEqual(set(rectangular_result), {"real", "imaginary"})
        self.assertAlmostEqual(rectangular_result["real"], 0.0)
        self.assertAlmostEqual(rectangular_result["imaginary"], 5.0)

        impedance_result = calculate_formula(
            "16",
            {"XC": 3.0, "XL": 7.0, "resistor": 4.0},
        )
        self.assertEqual(set(impedance_result), {"total_impedance", "phase_angle"})
        self.assertAlmostEqual(impedance_result["total_impedance"], math.sqrt(32))
        self.assertAlmostEqual(impedance_result["phase_angle"], 45.0)

        capacitive_result = calculate_formula(
            "17",
            {"capacitance": 0.1, "source_frequency": 10.0},
        )
        self.assertEqual(set(capacitive_result), {"capacitive_reactance"})
        self.assertAlmostEqual(
            capacitive_result["capacitive_reactance"],
            1 / (2 * math.pi),
        )

        inductive_result = calculate_formula(
            "18",
            {"inductance": 4.0, "source_frequency": 50.0},
        )
        self.assertEqual(set(inductive_result), {"inductive_reactance"})
        self.assertAlmostEqual(inductive_result["inductive_reactance"], 400 * math.pi)

    def test_unsupported_formula_option_raises_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported formula selection\\."):
            calculate_formula("19", {})


if __name__ == "__main__":
    unittest.main()
