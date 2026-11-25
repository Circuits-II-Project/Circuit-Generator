import os
import re
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, ".."))

from web import server

PAGE = os.path.join(HERE, "..", "web", "display.html")


class GuiFlowTests(unittest.TestCase):

    def setUp(self):
        patcher = mock.patch.object(server, "redraw")
        patcher.start()
        self.addCleanup(patcher.stop)
        server.reset_state()
        self.client = server.app.test_client()

    # --- the same clicks the page makes ---
    def add(self, comp_type, from_node, to_node, value, status=200):
        res = self.client.post(f"/add/{comp_type}",
                               json={"from_node": from_node, "to_node": to_node, "value": value})
        self.assertEqual(res.status_code, status, res.get_json())
        return res.get_json()

    def ground(self, node):
        res = self.client.post("/ground", json={"node": node})
        self.assertEqual(res.status_code, 200, res.get_json())
        return res.get_json()

    def calculate(self):
        res = self.client.post("/calculate")
        self.assertEqual(res.status_code, 200, res.get_json())
        return res.get_json()

    def test_series_circuit(self):
        self.add("resistor", "new", "new", 100)     # R1 N0-N1
        self.add("resistor", "N1", "new", 300)      # R2 N1-N2
        self.add("source", "N0", "N2", 12)          # V1 + on N0
        state = self.ground("N2")
        self.assertTrue(state["check"]["ok"])
        out = self.calculate()
        self.assertAlmostEqual(out["node_voltages"]["N1"], 9.0)
        self.assertAlmostEqual(out["components"]["R1"]["current"], 0.03)

    def test_parallel_circuit(self):
        self.add("resistor", "new", "new", 100)     # R1 N0-N1
        self.add("resistor", "N0", "N1", 100)       # R2 same nodes
        self.add("source", "N0", "N1", 10)
        self.ground("N1")
        out = self.calculate()
        self.assertAlmostEqual(out["components"]["R1"]["current"], 0.1)
        self.assertAlmostEqual(out["components"]["V1"]["current"], -0.2)

    def test_r1_series_with_r2_parallel_r3(self):
        self.add("resistor", "new", "new", 100)     # R1 N0-N1
        self.add("resistor", "N1", "new", 200)      # R2 N1-N2
        self.add("resistor", "N1", "N2", 300)       # R3 N1-N2
        self.add("source", "N0", "N2", 12)
        state = self.ground("N2")
        self.assertIn("Parallel: R2 ∥ R3", state["labels"])
        out = self.calculate()
        self.assertAlmostEqual(out["components"]["R1"]["current"], 12 / 220)

    def test_wheatstone_bridge(self):
        self.add("resistor", "new", "new", 100)     # R1 N0-N1  (N0 = top)
        self.add("resistor", "N1", "new", 200)      # R2 N1-N2  (N2 = bottom)
        self.add("resistor", "N0", "new", 100)      # R3 N0-N3
        self.add("resistor", "N3", "N2", 200)       # R4 N3-N2
        self.add("resistor", "N1", "N3", 500)       # R5 middle
        self.add("source", "N0", "N2", 10)
        self.ground("N2")
        out = self.calculate()
        self.assertAlmostEqual(out["components"]["R5"]["current"], 0.0)

    def test_calculate_is_blocked_until_check_passes(self):
        state = self.add("resistor", "new", "new", 100)
        self.assertFalse(state["check"]["ok"])
        self.assertTrue(state["check"]["problems"])
        res = self.client.post("/calculate")
        self.assertEqual(res.status_code, 400)
        self.assertIn("problems", res.get_json())

    def test_errors_show_and_app_keeps_working(self):
        self.add("resistor", "new", "new", 100)
        # Module 1 errors
        for bad in ({"from_node": "N1", "to_node": "N1", "value": 1},
                    {"from_node": "N0", "to_node": "N1", "value": -5},
                    {"from_node": "N0", "to_node": "N1", "value": 0},
                    {"from_node": "N0", "to_node": "N1"}):
            res = self.client.post("/add/resistor", json=bad)
            self.assertEqual(res.status_code, 400, bad)
            self.assertTrue(res.get_json()["error"])   # the page shows this text
        # Module 2 errors come back as a list
        self.assertEqual(self.client.post("/calculate").status_code, 400)
        # Still fine afterwards
        self.add("resistor", "N1", "N0", 100)
        self.add("source", "N0", "N1", 5)
        self.ground("N1")
        self.assertAlmostEqual(self.calculate()["components"]["V1"]["current"], -0.1)

    def test_remove_and_recalculate(self):
        self.add("resistor", "new", "new", 100)     # R1 N0-N1
        self.add("resistor", "N0", "N1", 100)       # R2 parallel
        self.add("source", "N0", "N1", 10)
        self.ground("N1")
        self.assertAlmostEqual(self.calculate()["components"]["V1"]["current"], -0.2)
        state = self.client.post("/remove/R2").get_json()
        self.assertTrue(state["check"]["ok"])
        self.assertAlmostEqual(self.calculate()["components"]["V1"]["current"], -0.1)

    def test_state_has_what_the_page_reads(self):
        state = self.add("resistor", "new", "new", 1000)
        for key in ("nodes", "components", "circuit", "ground", "check", "labels"):
            self.assertIn(key, state)
        self.assertEqual(state["circuit"]["components"][0]["resistance"], 1000.0)


class PageRoutesTests(unittest.TestCase):

    def test_every_route_the_page_calls_exists(self):
        with open(PAGE, encoding="utf-8") as f:
            html = f.read()
        called = set(re.findall(r"""(?:api|change)\("(?:GET|POST)",\s*"(/[a-z_]*)""", html))
        self.assertTrue(called, "no api(...) calls found in display.html")
        rules = [rule.rule for rule in server.app.url_map.iter_rules()]
        for route in called:
            self.assertTrue(any(r == route or r.startswith(route.rstrip("/") + "/") for r in rules),
                            f"display.html calls {route} but the server has no such route")


if __name__ == "__main__":
    unittest.main()