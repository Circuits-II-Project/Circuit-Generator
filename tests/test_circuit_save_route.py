from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from core.circuit_storage import load_circuits, resolve_diagram_path
from web import server


class SaveRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = TemporaryDirectory()
        root = Path(self.directory.name)
        self.storage = root / "saved_circuits.json"
        self.image = root / "working.png"
        self.storage_patcher = patch.object(server, "CIRCUIT_STORAGE_PATH", self.storage)
        self.image_patcher = patch.object(server, "IMAGE_PATH", self.image)
        self.storage_patcher.start()
        self.image_patcher.start()
        self.addCleanup(self.storage_patcher.stop)
        self.addCleanup(self.image_patcher.stop)
        self.addCleanup(self.directory.cleanup)
        server.reset_state()
        self.client = server.app.test_client()

    def post(self, route: str, body: dict) -> None:
        response = self.client.post(route, json=body)
        self.assertEqual(response.status_code, 200, response.get_json())

    def build_complete_circuit(self) -> None:
        self.post("/add/resistor", {"from_node": "new", "to_node": "new", "value": 100})
        self.post("/add/source", {"from_node": "N0", "to_node": "N1", "value": 10})
        self.post("/ground", {"node": "N1"})

    def save_new(self, name="Saved circuit") -> dict:
        response = self.client.post("/circuits", json={"circuit_name": name})
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["record"]

    def test_save_route_uses_the_current_circuit_and_current_diagram(self) -> None:
        self.build_complete_circuit()

        record = self.save_new("Lab circuit")
        record = load_circuits(self.storage)[0]
        self.assertEqual(record["circuit"], server.circuit_data)
        self.assertEqual(record["circuit_name"], "Lab circuit")
        self.assertTrue(resolve_diagram_path(self.storage, record).is_file())

    def test_list_get_load_and_continue_editing(self) -> None:
        self.build_complete_circuit()
        saved = self.save_new("Editable")
        summary_response = self.client.get("/circuits")
        self.assertEqual(summary_response.status_code, 200)
        self.assertEqual(summary_response.get_json()["circuits"][0]["record_id"], saved["record_id"])
        detail_response = self.client.get(f"/circuits/{saved['record_id']}")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.get_json()["record"]["circuit"], saved["circuit"])

        self.client.post("/reset")
        loaded = self.client.post(f"/circuits/{saved['record_id']}/load")
        self.assertEqual(loaded.status_code, 200, loaded.get_json())
        self.assertEqual(loaded.get_json()["state"]["loaded_record_id"], saved["record_id"])
        self.assertEqual(self.client.post("/calculate").status_code, 200)
        self.post("/add/resistor", {"from_node": "N1", "to_node": "new", "value": 220})
        self.assertEqual(server.circuit_data["components"][-1]["to_node"], "N2")

    def test_update_loaded_record_does_not_create_a_duplicate(self) -> None:
        self.build_complete_circuit()
        saved = self.save_new("Before update")
        self.post("/add/source", {"from_node": "N0", "to_node": "N1", "value": 12})

        response = self.client.put(
            f"/circuits/{saved['record_id']}", json={"circuit_name": "After update"},
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        records = load_circuits(self.storage)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["record_id"], saved["record_id"])
        self.assertEqual(records[0]["circuit_name"], "After update")
        self.assertEqual(records[0]["circuit"]["source"]["source_voltage"], 12.0)

    def test_load_missing_image_rebuilds_from_data_and_returns_warning(self) -> None:
        self.build_complete_circuit()
        saved = self.save_new()
        resolve_diagram_path(self.storage, saved).unlink()

        response = self.client.post(f"/circuits/{saved['record_id']}/load")
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertFalse(response.get_json()["image_available"])
        self.assertIn("warning", response.get_json())
        self.assertEqual(server.circuit_data, saved["circuit"])

    def test_unknown_or_corrupt_saved_record_does_not_change_live_state(self) -> None:
        self.build_complete_circuit()
        before = server.state_json()
        missing = self.client.post("/circuits/not-here/load")
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(server.state_json(), before)

        self.storage.write_text("{broken", encoding="utf-8")
        corrupt = self.client.get("/circuits")
        self.assertEqual(corrupt.status_code, 400)
        self.assertEqual(server.state_json(), before)


if __name__ == "__main__":
    unittest.main()
