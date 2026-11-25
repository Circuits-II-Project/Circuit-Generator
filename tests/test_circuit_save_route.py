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

    def test_save_route_uses_the_current_circuit_and_current_diagram(self) -> None:
        self.post("/add/resistor", {"from_node": "new", "to_node": "new", "value": 100})
        self.post("/add/source", {"from_node": "N0", "to_node": "N1", "value": 10})
        self.post("/ground", {"node": "N1"})

        response = self.client.post("/save")
        self.assertEqual(response.status_code, 201, response.get_json())
        record = load_circuits(self.storage)[0]
        self.assertEqual(record["circuit"], server.circuit_data)
        self.assertTrue(resolve_diagram_path(self.storage, record).is_file())


if __name__ == "__main__":
    unittest.main()
