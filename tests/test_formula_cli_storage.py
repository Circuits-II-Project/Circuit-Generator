import io
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from formula_cli import main
from formula_storage import load_calculations


class FormulaCliStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.storage_path = Path(self.temporary_directory.name) / "calculations.json"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_cli(self, responses: list[object]) -> str:
        output = io.StringIO()
        with patch("builtins.input", side_effect=responses):
            with redirect_stdout(output):
                main(self.storage_path)
        return output.getvalue()

    def test_saves_real_dc_and_ac_calculations(self) -> None:
        dc_output = self.run_cli(["1", "0.005", "100", "s"])
        ac_output = self.run_cli(["17", "0.1", "10", "s"])

        calculations = load_calculations(self.storage_path)
        self.assertEqual(len(calculations), 2)
        self.assertEqual(calculations[0]["inputs"], {"current": 0.005, "resistance": 100.0})
        self.assertEqual(calculations[0]["results"], {"resistor_voltage": 0.5})
        self.assertEqual(
            calculations[1]["inputs"],
            {"capacitance": 0.1, "source_frequency": 10.0},
        )
        self.assertEqual(calculations[1]["diagram_path"], None)
        self.assertIn("Cálculo guardado correctamente.", dc_output)
        self.assertIn("Cálculo guardado correctamente.", ac_output)

    def test_declining_save_does_not_create_a_file(self) -> None:
        output = self.run_cli(["1", "1", "2", "n"])

        self.assertFalse(self.storage_path.exists())
        self.assertNotIn("Cálculo guardado correctamente.", output)

    def test_invalid_save_response_is_repeated_until_valid(self) -> None:
        output = self.run_cli(["1", "1", "2", "maybe", "s"])

        self.assertIn("Responde con s para guardar o n para no guardar.", output)
        self.assertEqual(len(load_calculations(self.storage_path)), 1)

    def test_eof_at_save_prompt_declines_without_creating_a_file(self) -> None:
        output = self.run_cli(["1", "1", "2", EOFError()])

        self.assertIn("resistor_voltage: 2.0", output)
        self.assertFalse(self.storage_path.exists())

    def test_storage_failure_keeps_result_and_existing_file(self) -> None:
        self.storage_path.write_text("{invalid", encoding="utf-8")
        before = self.storage_path.read_bytes()

        output = self.run_cli(["1", "1", "2", "s"])

        self.assertIn("resistor_voltage: 2.0", output)
        self.assertIn("No se pudo guardar el cálculo:", output)
        self.assertNotIn("Cálculo guardado correctamente.", output)
        self.assertEqual(self.storage_path.read_bytes(), before)

    def test_failed_calculation_does_not_offer_saving(self) -> None:
        with (
            patch("formula_cli.calculate_formula", side_effect=ZeroDivisionError("zero")),
            patch("formula_cli.should_save_calculation") as save_prompt,
        ):
            output = self.run_cli(["1", "1", "2"])

        self.assertIn("Error de cálculo: zero", output)
        save_prompt.assert_not_called()
        self.assertFalse(self.storage_path.exists())


if __name__ == "__main__":
    unittest.main()
