import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from core.circuit_storage import (
    CircuitStorageError,
    circuit_identity,
    get_circuit,
    list_circuits,
    load_circuits,
    resolve_diagram_path,
    save_circuit,
    update_circuit,
)
from core.formula_storage import append_calculation, load_calculations


PNG_A = b"\x89PNG\r\n\x1a\nfirst image"
PNG_B = b"\x89PNG\r\n\x1a\nsecond image"


def circuit(resistance: float = 100.0) -> dict:
    return {
        "components": [{
            "component_id": "R1", "component_type": "resistor",
            "from_node": "N0", "to_node": "N1", "resistance": resistance,
        }],
        "source": {
            "source_id": "V1", "source_type": "DC", "source_voltage": 10.0,
            "source_frequency": None, "from_node": "N0", "to_node": "N1",
        },
        "ground": "N1",
    }


def results() -> dict:
    return {"ground": "N1", "node_voltages": {"N0": 10.0, "N1": 0.0}}


class CircuitStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.storage = self.root / "saved_circuits.json"
        self.working_image = self.root / "working.png"
        self.working_image.write_bytes(PNG_A)

    def tearDown(self) -> None:
        self.directory.cleanup()

    def save(self, resistance: float = 100.0, name: str = "Example circuit") -> dict:
        return save_circuit(
            self.storage, name, circuit(resistance), results(), self.working_image,
            {"next_node": 2, "last_node": "N1"},
        )

    def test_saves_real_circuit_results_and_image_as_one_record(self) -> None:
        record = self.save()
        image = resolve_diagram_path(self.storage, record)

        self.assertEqual(record["circuit"], circuit())
        self.assertEqual(record["results"], results())
        self.assertEqual(record["circuit_name"], "Example circuit")
        self.assertTrue(record["record_id"])
        self.assertEqual(image.read_bytes(), PNG_A)
        self.assertEqual(load_circuits(self.storage), [record])

    def test_saved_image_survives_a_later_working_image_overwrite(self) -> None:
        first = self.save()
        first_image = resolve_diagram_path(self.storage, first)
        self.working_image.write_bytes(PNG_B)
        second = self.save(220.0)

        self.assertEqual(first_image.read_bytes(), PNG_A)
        self.assertEqual(resolve_diagram_path(self.storage, second).read_bytes(), PNG_B)

    def test_successive_saves_do_not_collide_or_discard_records(self) -> None:
        first = self.save()
        second = self.save()
        records = load_circuits(self.storage)

        self.assertEqual(records, [first, second])
        self.assertNotEqual(first["diagram_path"], second["diagram_path"])
        self.assertTrue(resolve_diagram_path(self.storage, first).exists())
        self.assertTrue(resolve_diagram_path(self.storage, second).exists())

    def test_repeated_names_are_allowed_but_record_ids_are_unique(self) -> None:
        first = self.save(name="Lab circuit")
        second = self.save(name="Lab circuit")
        summaries = list_circuits(self.storage)

        self.assertEqual([item["circuit_name"] for item in summaries], ["Lab circuit", "Lab circuit"])
        self.assertNotEqual(first["record_id"], second["record_id"])

    def test_empty_name_is_rejected_without_creating_storage(self) -> None:
        with self.assertRaisesRegex(CircuitStorageError, "circuit_name"):
            self.save(name="  ")
        self.assertFalse(self.storage.exists())

    def test_filename_collision_never_replaces_an_existing_saved_image(self) -> None:
        fixed_uuid = SimpleNamespace(hex="fixed")
        with patch("core.circuit_storage.uuid.uuid4", return_value=fixed_uuid):
            first = self.save()
            first_image = resolve_diagram_path(self.storage, first)
            before = self.storage.read_bytes()
            with self.assertRaises(FileExistsError):
                self.save()

        self.assertEqual(first_image.read_bytes(), PNG_A)
        self.assertEqual(self.storage.read_bytes(), before)

    def test_relative_paths_are_resolved_from_the_collection_directory(self) -> None:
        record = self.save()
        resolved = resolve_diagram_path(self.storage, record)

        self.assertEqual(resolved, self.root / Path(record["diagram_path"]))
        self.assertFalse(Path(record["diagram_path"]).is_absolute())

    def test_get_and_update_keep_record_identity_and_prior_image(self) -> None:
        original = self.save(name="Original")
        original_image = resolve_diagram_path(self.storage, original)
        self.working_image.write_bytes(PNG_B)
        updated = update_circuit(
            self.storage, original["record_id"], circuit(220.0), results(), self.working_image,
            {"next_node": 2, "last_node": "N1"}, "Renamed",
        )

        self.assertEqual(updated["record_id"], original["record_id"])
        self.assertEqual(updated["circuit_name"], "Renamed")
        self.assertEqual(len(load_circuits(self.storage)), 1)
        self.assertEqual(get_circuit(self.storage, original["record_id"]), updated)
        self.assertEqual(original_image.read_bytes(), PNG_A)
        self.assertEqual(resolve_diagram_path(self.storage, updated).read_bytes(), PNG_B)

    def test_unknown_record_id_does_not_change_existing_data(self) -> None:
        self.save()
        before = self.storage.read_bytes()
        with self.assertRaisesRegex(CircuitStorageError, "not found"):
            update_circuit(
                self.storage, "missing", circuit(), results(), self.working_image,
                {"next_node": 2, "last_node": "N1"},
            )
        self.assertEqual(self.storage.read_bytes(), before)

    def test_legacy_formula_record_without_an_image_remains_readable(self) -> None:
        legacy_storage = self.root / "formulas.json"
        append_calculation(legacy_storage, "1", "Formula", {"current": 1}, {"voltage": 2})

        self.assertIsNone(load_calculations(legacy_storage)[0]["diagram_path"])

    def test_legacy_circuit_records_get_a_derived_name_and_id_without_rewrite(self) -> None:
        legacy = {
            "schema_version": 1,
            "circuits": [{
                "circuit_id": "", "circuit": circuit(), "results": results(),
                "diagram_path": "saved_circuit_images/old.png",
            }],
        }
        legacy["circuits"][0]["circuit_id"] = circuit_identity(circuit())
        self.storage.write_text(json.dumps(legacy), encoding="utf-8")
        before = self.storage.read_bytes()

        record = load_circuits(self.storage)[0]
        self.assertEqual(record["circuit_name"], "Untitled circuit 1")
        self.assertTrue(record["record_id"])
        self.assertEqual(self.storage.read_bytes(), before)

    def test_missing_or_invalid_source_image_preserves_prior_data(self) -> None:
        self.save()
        before = self.storage.read_bytes()
        self.working_image.unlink()
        with self.assertRaisesRegex(CircuitStorageError, "No current diagram"):
            self.save(220.0)
        self.assertEqual(self.storage.read_bytes(), before)

        self.working_image.write_text("not an image", encoding="utf-8")
        with self.assertRaisesRegex(CircuitStorageError, "valid PNG"):
            self.save(220.0)
        self.assertEqual(self.storage.read_bytes(), before)

    def test_copy_failure_preserves_records_and_creates_no_new_image(self) -> None:
        first = self.save()
        before = self.storage.read_bytes()
        before_images = list((self.root / "saved_circuit_images").iterdir())
        with patch("core.circuit_storage._copy_image_exclusively", side_effect=OSError("copy failed")):
            with self.assertRaises(OSError):
                self.save(220.0)

        self.assertEqual(self.storage.read_bytes(), before)
        self.assertEqual(list((self.root / "saved_circuit_images").iterdir()), before_images)
        self.assertEqual(load_circuits(self.storage), [first])

    def test_json_write_failure_preserves_records_and_removes_new_image(self) -> None:
        first = self.save()
        before = self.storage.read_bytes()
        before_images = list((self.root / "saved_circuit_images").iterdir())
        with patch("core.circuit_storage.os.replace", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.save(220.0)

        self.assertEqual(self.storage.read_bytes(), before)
        self.assertEqual(list((self.root / "saved_circuit_images").iterdir()), before_images)
        self.assertEqual(load_circuits(self.storage), [first])


if __name__ == "__main__":
    unittest.main()
