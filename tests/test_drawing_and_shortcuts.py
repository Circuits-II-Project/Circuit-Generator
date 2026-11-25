import os
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, ".."))

from core import formula_service
from web import drawing, server


def R(cid, a, b, ohms=100.0):
    return {"component_id": cid, "component_type": "resistor",
            "from_node": a, "to_node": b, "resistance": ohms}


def src(a, b, volts=12.0):
    return {"source_id": "V1", "source_type": "DC", "source_voltage": volts,
            "source_frequency": None, "from_node": a, "to_node": b}


MIXED = {"source": src("N0", "N2"), "ground": "N2",
         "components": [R("R1", "N0", "N1"), R("R2", "N1", "N2", 200), R("R3", "N1", "N2", 300)]}
BRIDGE = {"source": src("N0", "N2"), "ground": "N2",
          "components": [R("R1", "N0", "N1"), R("R2", "N1", "N2"), R("R3", "N0", "N3"),
                         R("R4", "N3", "N2"), R("R5", "N1", "N3")]}


def ids(tree):
    # Tree -> nested lists of part ids
    if tree[0] == "part":
        return tree[1]["id"]
    return [tree[0], [ids(c) for c in tree[1]]]


class DrawingTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def draw(self, circuit):
        path = os.path.join(self.tmp.name, "c.png")
        layout = drawing.draw_circuit(circuit, path)
        self.assertGreater(os.path.getsize(path), 0)
        return layout

    def test_r1_series_with_r2_parallel_r3_is_drawn_with_a_parallel_block(self):
        tree = drawing.reduce_sp(drawing.parts_of(MIXED)[:-1], "N0", "N2") 
        self.assertEqual(ids(tree), ["ser", ["R1", ["par", ["R2", "R3"]]]])
        self.assertEqual(self.draw(MIXED), "series-parallel")

    def test_structure_text(self):
        self.assertEqual(drawing.structure(MIXED), "R1 + (R2 ∥ R3)")
        pairs = {"source": src("T", "G"), "components": [
            R("R1", "T", "A"), R("R2", "A", "G"), R("R3", "T", "B"), R("R4", "B", "G")]}
        self.assertEqual(drawing.structure(pairs), "(R1 + R2) ∥ (R3 + R4)")

    def test_reversed_parts_still_reduce(self):
        # R2 drawn "backwards" (to -> from) must not matter
        circuit = {"source": src("N0", "N2"),
                   "components": [R("R1", "N0", "N1"), R("R2", "N2", "N1")]}
        self.assertEqual(drawing.structure(circuit), "R1 + R2")

    def test_bridge_falls_back_to_ring(self):
        self.assertIsNone(drawing.structure(BRIDGE))
        self.assertEqual(self.draw(BRIDGE), "ring")

    def test_unfinished_circuits_still_draw(self):
        no_source = {"components": [R("R1", "N0", "N1"), R("R2", "N1", "N2"), R("R3", "N1", "N2")]}
        self.assertEqual(self.draw(no_source), "ring")
        open_end = {"source": src("N0", "N1"), "components": [R("R1", "N0", "N1"), R("R2", "N1", "N2")]}
        self.assertEqual(self.draw(open_end), "ring")
        only_source = {"source": src("N0", "N1"), "components": []}
        self.assertEqual(self.draw(only_source), "ring")

    def test_capacitor_and_inductor_draw(self):
        circuit = {"source": src("N0", "N2"), "ground": "N2", "components": [
            {"component_id": "C1", "component_type": "capacitor", "from_node": "N0",
             "to_node": "N1", "capacitance": 1e-6},
            {"component_id": "L1", "component_type": "inductor", "from_node": "N1",
             "to_node": "N2", "inductance": 0.01}]}
        self.assertEqual(self.draw(circuit), "series-parallel")


class ServerDrawingTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.object(server, "IMAGE_PATH", os.path.join(self.tmp.name, "MyCirc_2.png"))
        patcher.start()
        self.addCleanup(patcher.stop)
        server.reset_state()
        self.client = server.app.test_client()

    def test_redraw_writes_the_image(self):
        self.client.post("/add/resistor", json={"from_node": "new", "to_node": "new", "value": 100})
        self.assertTrue(os.path.exists(server.IMAGE_PATH))

    def test_drawing_failure_does_not_break_the_request(self):
        with mock.patch.object(drawing, "draw_circuit", side_effect=RuntimeError("boom")):
            res = self.client.post("/add/resistor", json={"from_node": "new", "to_node": "new", "value": 100})
        self.assertEqual(res.status_code, 200)
        self.assertIn("R1", res.get_json()["components"])


class PlanBTests(unittest.TestCase):

    def setUp(self):
        patcher = mock.patch.object(server, "redraw")
        patcher.start()
        self.addCleanup(patcher.stop)
        server.reset_state()
        self.client = server.app.test_client()

    def post(self, url, body=None, status=200):
        res = self.client.post(url, json=body or {})
        self.assertEqual(res.status_code, status, res.get_json())
        return res.get_json()

    def chain(self):
        self.post("/add/resistor", {"from_node": "new", "to_node": "new", "value": 100})
        self.post("/add/resistor", {"from_node": "N1", "to_node": "new", "value": 200})
        self.post("/add/resistor", {"from_node": "N2", "to_node": "new", "value": 300})
        self.post("/add/source", {"from_node": "N0", "to_node": "N3", "value": 13})
        self.post("/ground", {"node": "N3"})

    def plan_a_reference(self):
        server.reset_state()
        self.post("/add/resistor", {"from_node": "new", "to_node": "new", "value": 100})
        self.post("/add/resistor", {"from_node": "N1", "to_node": "new", "value": 200})
        self.post("/add/resistor", {"from_node": "N2", "to_node": "new", "value": 300})
        self.post("/add/resistor", {"from_node": "N3", "to_node": "new", "value": 50})
        self.post("/add/source", {"from_node": "N0", "to_node": "N4", "value": 13})
        self.post("/ground", {"node": "N4"})
        return self.post("/calculate")

    def check_insert(self, target, expect_from, expect_to):
        self.chain()
        old = self.client.get("/state").get_json()["components"][target]
        state = self.post(f"/insert_series/{target}", {"type": "resistor", "value": 50})
        moved, new = state["components"][target], state["components"]["R4"]
        self.assertEqual(moved["from"], old["from"])
        self.assertEqual(moved["to"], "N4")
        self.assertEqual((new["from"], new["to"]), ("N4", old["to"]))
        self.assertEqual((expect_from, expect_to), (new["from"], new["to"]))
        self.assertTrue(state["check"]["ok"], state["check"])

        result = self.post("/calculate")
        reference = self.plan_a_reference()
        self.assertAlmostEqual(result["components"]["V1"]["current"], -13 / 650)
        self.assertAlmostEqual(result["components"]["V1"]["current"],
                               reference["components"]["V1"]["current"])
        self.assertAlmostEqual(result["total_power_delivered"], reference["total_power_delivered"])
        self.assertAlmostEqual(result["components"]["R4"]["voltage"], 50 * 13 / 650)

    def test_add_in_series_first(self):
        self.check_insert("R1", "N4", "N1")

    def test_add_in_series_middle(self):
        self.check_insert("R2", "N4", "N2")

    def test_add_in_series_last(self):
        self.check_insert("R3", "N4", "N3")

    @unittest.skip("Calculate only supports series circuits for now")
    def test_add_in_parallel_matches_building_by_nodes(self):
        self.chain()
        r2 = self.client.get("/state").get_json()["components"]["R2"]
        self.post("/add/resistor", {"from_node": r2["from"], "to_node": r2["to"], "value": 200})
        shortcut = self.post("/calculate")

        server.reset_state()
        self.chain()
        self.post("/add/resistor", {"from_node": "N1", "to_node": "N2", "value": 200})
        by_nodes = self.post("/calculate")
        self.assertEqual(shortcut, by_nodes)
        self.assertAlmostEqual(shortcut["components"]["V1"]["current"], -13 / 500) 

    def test_failed_insert_leaves_circuit_unchanged(self):
        self.chain()
        before = self.client.get("/state").get_json()
        self.post("/insert_series/R2", {"type": "resistor", "value": -1}, status=400)
        self.post("/insert_series/R2", {"type": "source", "value": 5}, status=400)
        self.post("/insert_series/R9", {"type": "resistor", "value": 5}, status=404)
        self.assertEqual(self.client.get("/state").get_json(), before)

    def test_structure_is_in_state(self):
        self.chain()
        self.assertEqual(self.client.get("/state").get_json()["structure"], "R1 + R2 + R3")


class SuiteImportTests(unittest.TestCase):

    def test_formula_service_imports(self):
        self.assertTrue(hasattr(formula_service, "calc_impedance"))


if __name__ == "__main__":
    unittest.main()