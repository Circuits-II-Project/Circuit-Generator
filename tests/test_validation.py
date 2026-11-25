import os
import sys 
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, ".."))

from core.validation import check_circuit
from web import server


def resistor(rid, a, b, r=100.0):
    return {"component_id": rid, "component_type": "resistor",
            "from_node": a, "to_node": b, "resistance": r}


def source(a="N0", b="N1", volts=12.0):
    return {"source_id": "V1", "source_type": "DC", "source_voltage": volts,
            "source_frequency": None, "from_node": a, "to_node": b}


def good_circuit():
    return {"source": source(), "ground": "N1",
            "components": [resistor("R1", "N0", "N2"), resistor("R2", "N2", "N1")]}

class CheckCircuitTests(unittest.TestCase):

    def test_complete_circuit_is_ok(self):
        self.assertEqual(check_circuit(good_circuit()), [])

    def test_parallel_and_bridge_circuits_are_ok(self):
        bridge = {"source": source("T", "G"), "ground": "G", "components": [
            resistor("R1", "T", "A"), resistor("R2", "A", "G"),
            resistor("R3", "T", "B"), resistor("R4", "B", "G"),
            resistor("R5", "A", "B")]}
        self.assertEqual(check_circuit(bridge), [])

    def test_no_source(self):
        circuit = good_circuit()
        circuit["source"] = None
        circuit["components"].append(resistor("R3", "N0", "N1"))   
        problems = check_circuit(circuit)
        self.assertEqual(len(problems), 1)
        self.assertIn("no voltage source", problems[0])

    def test_no_ground(self):
        circuit = good_circuit()
        del circuit["ground"]
        problems = check_circuit(circuit)
        self.assertEqual(len(problems), 1)
        self.assertIn("No ground node", problems[0])

    def test_ground_not_in_circuit(self):
            circuit = good_circuit()
            circuit["ground"] = "N9"
            self.assertIn("N9 is not connected", check_circuit(circuit)[0])

    def test_open_end_names_the_node(self):
        circuit = good_circuit()
        circuit["components"].append(resistor("R3", "N2", "N3"))   
        problems = check_circuit(circuit)
        self.assertEqual(len(problems), 1)
        self.assertIn("Node N3 is an open end", problems[0])
        self.assertIn("R3", problems[0])

    def test_disconnected_piece(self):
        circuit = good_circuit()
        # A separate closed loop: N5 and N6 each have 2 ends, but nothing reaches ground
        circuit["components"] += [resistor("R3", "N5", "N6"), resistor("R4", "N5", "N6")]
        problems = check_circuit(circuit)
        self.assertEqual(len(problems), 1)
        self.assertIn("not connected to ground (N1): N5, N6", problems[0])

    def test_empty_circuit(self):
        self.assertIn("empty", check_circuit({"components": []})[0])

    def test_several_problems_are_all_listed(self):
        circuit = {"components": [resistor("R1", "N0", "N1")]}    #no source, no ground, 2 open ends
        self.assertEqual(len(check_circuit(circuit)), 4)

    def test_bad_data_becomes_a_problem_not_a_crash(self):
        problems = check_circuit({"components": [resistor("R1", "A", "A")]})
        self.assertIn("invalid", problems[0])

class CheckRouteTests(unittest.TestCase):

    def setUp(self):
        patcher = mock.patch.object(server, "redraw")
        patcher.start()
        self.addCleanup(patcher.stop)
        server.reset_state()
        self.client = server.app.test_client()

    def test_check_route_reports_problems_then_ok(self):
        self.assertFalse(self.client.get("/check").get_json()["ok"])

        c = self.client
        c.post("/add/resistor", json={"from_node": "new", "to_node": "new", "value": 100})  # N0-N1
        c.post("/add/resistor", json={"from_node": "N1", "to_node": "new", "value": 100})  # N1-N2
        c.post("/add/source", json={"from_node": "N0", "to_node": "N2", "value": 10})
        state = c.post("/ground", json={"node": "N2"}).get_json()

        self.assertEqual(state["check"], {"ok": True, "problems": []})
        self.assertEqual(c.get("/check").get_json(), {"ok": True, "problems": []})


if __name__ == "__main__":
    unittest.main()
