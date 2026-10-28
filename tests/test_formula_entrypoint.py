import subprocess
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FormulaEntrypointTests(unittest.TestCase):
    def test_importing_formula_modules_has_no_terminal_interaction(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import formula_service; import formula_cli; import formula_input_test",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_existing_entrypoint_runs_formula_cli(self) -> None:
        result = subprocess.run(
            [sys.executable, "formula_input_test.py"],
            cwd=ROOT,
            input="17\n0.1\n10\n",
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("AC - Capacitive reactance", result.stdout)
        self.assertIn("capacitive_reactance: 0.15915494309189535", result.stdout)


if __name__ == "__main__":
    unittest.main()
