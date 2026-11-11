import copy
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from formula_service import FORMULAS, calculate_formula
from formula_storage import StorageFormatError, append_calculation, load_calculations


class FormulaStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.storage_path = Path(self.temporary_directory.name) / "calculations.json"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def append_service_calculation(
        self,
        option: str,
        inputs: dict[str, object],
        diagram_path: str | None = None,
    ) -> dict[str, object]:
        return append_calculation(
            self.storage_path,
            option,
            FORMULAS[option][0],
            inputs,
            calculate_formula(option, inputs),
            diagram_path,
        )

    def valid_record(self) -> dict[str, object]:
        return {
            "formula_option": "1",
            "formula_name": FORMULAS["1"][0],
            "inputs": {"current": 1.0, "resistance": 2.0},
            "results": {"resistor_voltage": 2.0},
            "diagram_path": None,
        }

    def assert_persisted_record_is_rejected(
        self,
        record: dict[str, object],
        error_type: type[Exception],
    ) -> None:
        document = {"schema_version": 1, "calculations": [record]}
        self.storage_path.write_text(json.dumps(document), encoding="utf-8")
        before = self.storage_path.read_bytes()

        with self.assertRaises(error_type):
            load_calculations(self.storage_path)
        with self.assertRaises(error_type):
            self.append_service_calculation("1", {"current": 1.0, "resistance": 2.0})

        self.assertEqual(self.storage_path.read_bytes(), before)

    def test_missing_and_empty_files_read_as_empty_without_writing(self) -> None:
        self.assertEqual(load_calculations(self.storage_path), [])
        self.assertFalse(self.storage_path.exists())

        self.storage_path.write_text("", encoding="utf-8")
        self.assertEqual(load_calculations(self.storage_path), [])
        self.assertEqual(self.storage_path.read_text(encoding="utf-8"), "")

    def test_saves_and_loads_real_dc_and_ac_service_results(self) -> None:
        dc_inputs = {"current": 0.005, "resistance": 100.0}
        ac_inputs = {"capacitance": 0.1, "source_frequency": 10.0}
        self.append_service_calculation("1", dc_inputs)
        self.append_service_calculation("17", ac_inputs)

        calculations = load_calculations(self.storage_path)
        self.assertEqual(len(calculations), 2)
        self.assertEqual(calculations[0]["inputs"], dc_inputs)
        self.assertEqual(calculations[0]["results"], {"resistor_voltage": 0.5})
        self.assertEqual(calculations[1]["inputs"], ac_inputs)
        self.assertAlmostEqual(
            calculations[1]["results"]["capacitive_reactance"],
            1 / (2 * math.pi),
        )

        document = json.loads(self.storage_path.read_text(encoding="utf-8"))
        self.assertEqual(document["schema_version"], 1)
        self.assertEqual(document["calculations"], calculations)

    def test_diagram_path_is_optional_and_can_be_relative(self) -> None:
        self.append_service_calculation("1", {"current": 1.0, "resistance": 2.0})
        self.append_service_calculation(
            "1",
            {"current": 2.0, "resistance": 3.0},
            "diagrams/circuit-001.png",
        )

        calculations = load_calculations(self.storage_path)
        self.assertIsNone(calculations[0]["diagram_path"])
        self.assertEqual(calculations[1]["diagram_path"], "diagrams/circuit-001.png")

    def test_corrupt_and_incompatible_files_raise_without_changes(self) -> None:
        for content in (
            "{not valid json",
            json.dumps({"schema_version": 2, "calculations": []}),
        ):
            with self.subTest(content=content):
                self.storage_path.write_text(content, encoding="utf-8")
                before = self.storage_path.read_bytes()
                with self.assertRaises(StorageFormatError):
                    load_calculations(self.storage_path)
                with self.assertRaises(StorageFormatError):
                    self.append_service_calculation(
                        "1", {"current": 1.0, "resistance": 2.0}
                    )
                self.assertEqual(self.storage_path.read_bytes(), before)

    def test_rejects_invalid_values_without_overwriting_saved_records(self) -> None:
        self.append_service_calculation("1", {"current": 1.0, "resistance": 2.0})
        before = self.storage_path.read_bytes()

        invalid_cases = (
            ({"current": math.nan}, {"resistor_voltage": 1.0}, ValueError),
            ({"current": 1.0}, {"resistor_voltage": {1, 2}}, TypeError),
        )
        for inputs, results, error_type in invalid_cases:
            with self.subTest(inputs=inputs, results=results):
                with self.assertRaises(error_type):
                    append_calculation(
                        self.storage_path,
                        "1",
                        FORMULAS["1"][0],
                        inputs,
                        results,
                    )
                self.assertEqual(self.storage_path.read_bytes(), before)

    def test_rejects_non_finite_values_in_persisted_inputs_or_results(self) -> None:
        locations = ("inputs", "results")
        values = (math.nan, math.inf, -math.inf)

        for location in locations:
            for value in values:
                with self.subTest(location=location, value=value):
                    record = self.valid_record()
                    record[location] = {"value": value}
                    self.assert_persisted_record_is_rejected(record, ValueError)

    def test_rejects_persisted_records_missing_required_fields(self) -> None:
        for field in (
            "formula_option",
            "formula_name",
            "inputs",
            "results",
            "diagram_path",
        ):
            with self.subTest(field=field):
                record = self.valid_record()
                record.pop(field)
                self.assert_persisted_record_is_rejected(record, StorageFormatError)

    def test_rejects_incorrect_persisted_record_field_types(self) -> None:
        invalid_fields = {
            "formula_option": 1,
            "formula_name": None,
            "inputs": [],
            "results": [],
            "diagram_path": 1,
        }
        for field, value in invalid_fields.items():
            with self.subTest(field=field):
                record = self.valid_record()
                record[field] = value
                self.assert_persisted_record_is_rejected(record, StorageFormatError)

    def test_rejects_absolute_persisted_diagram_paths(self) -> None:
        absolute_paths = (
            r"C:\diagrams\circuit.png",
            r"\\server\share\circuit.png",
        )
        for diagram_path in absolute_paths:
            with self.subTest(diagram_path=diagram_path):
                record = self.valid_record()
                record["diagram_path"] = diagram_path
                self.assert_persisted_record_is_rejected(record, StorageFormatError)

    def test_failed_atomic_replacement_preserves_records_and_cleans_temporary_file(
        self,
    ) -> None:
        self.append_service_calculation("1", {"current": 1.0, "resistance": 2.0})
        before = self.storage_path.read_bytes()

        with patch("formula_storage.os.replace", side_effect=OSError("disk failure")):
            with self.assertRaises(OSError):
                self.append_service_calculation(
                    "17",
                    {"capacitance": 0.1, "source_frequency": 10.0},
                )

        self.assertEqual(self.storage_path.read_bytes(), before)
        self.assertEqual(list(self.storage_path.parent.glob(".calculations.json.*.tmp")), [])

    def test_append_does_not_mutate_received_inputs_or_results(self) -> None:
        inputs = {"values": [1.0, {"nested": 2.0}]}
        results = {"result": [3.0, {"nested": 4.0}]}
        original_inputs = copy.deepcopy(inputs)
        original_results = copy.deepcopy(results)

        append_calculation(
            self.storage_path,
            "custom",
            "Custom formula",
            inputs,
            results,
        )

        self.assertEqual(inputs, original_inputs)
        self.assertEqual(results, original_results)
