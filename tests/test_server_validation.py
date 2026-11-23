import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE,".."))
sys.path.append(os.path.join(HERE, "..", "GUI")) 

from node_calculations import loader as cl
import server

def resistor(rid, a, b, r=100.0):
    return {"component_id": rid, "component_type": "resistor",
            "from_node": a, "to_node": b, "resistance": r}


class ValidateComponentTests(unittest.TestCase):
    """validate_component() on its own (no server)."""

    def assertRejected(self, *args, contains):
        with self.assertRaises(ValueError) as ctx:
            cl.validate_component(*args)
        self.assertIn(contains, str(ctx.exception))

    def test_valid_component_returns_float(self):
        self.assertEqual(cl.validate_component("resistor", "N0", "N1", 100), 100.0)

    def test_source_type_is_allowed(self):
        self.assertEqual(cl.validate_component("source", "N0", "N1", 12), 12.0)

    def test_unknown_type(self):
        self.assertRejected("diode", "N0", "N1", 1, contains="Unknown component type 'diode'")

    def test_same_node_both_ends(self):
        self.assertRejected("resistor", "N1", "N1", 100,
                            contains="A component cannot connect a node to itself")

    def test_zero_value(self):
        self.assertRejected("resistor", "N0", "N1", 0, contains="greater than 0")

    def test_negative_value(self):
        self.assertRejected("resistor", "N0", "N1", -5, contains="greater than 0")

    def test_non_numeric_value(self):
        self.assertRejected("resistor", "N0", "N1", "abc", contains="must be a number")

    def test_bool_is_not_a_number(self):
        self.assertRejected("resistor", "N0", "N1", True, contains="must be a number")

    def test_nan_and_infinity(self):
        self.assertRejected("resistor", "N0", "N1", float("nan"), contains="finite")
        self.assertRejected("resistor", "N0", "N1", float("inf"), contains="finite")

    def test_missing_fields(self):
        self.assertRejected(None, "N0", "N1", 1, contains="Missing field: component type")
        self.assertRejected("resistor", None, "N1", 1, contains="Missing field: from_node")
        self.assertRejected("resistor", "N0", "", 1, contains="Missing field: to_node")
        self.assertRejected("resistor", "N0", "N1", None, contains="Missing field: value")

    def test_loader_rejects_bad_value_from_json_data(self):
        with self.assertRaises(ValueError):
            cl.components_loader({"components": [resistor("R1", "A", "B", r=-5)]})


class IdSortTests(unittest.TestCase):

    def test_ids_sort_by_number(self):
        self.assertEqual(sorted(["R10", "R2", "R1"], key=cl.id_sort_key), ["R1", "R2", "R10"])

    def test_node_names_sort_by_number(self):
        self.assertEqual(sorted(["N10", "N2", "N0"], key=cl.id_sort_key), ["N0", "N2", "N10"])


class ServerTests(unittest.TestCase):
    """Uses Flask's test client, so no browser or running server is needed."""

    def setUp(self):
        # Don't write images while testing
        patcher = mock.patch.object(server, "redraw")
        patcher.start()
        self.addCleanup(patcher.stop)
        server.reset_state()
        self.client = server.app.test_client()

    def add(self, comp_type, **body):
        return self.client.post(f"/add/{comp_type}", json=body)

    def test_add_chains_new_nodes(self):
        self.assertEqual(self.add("resistor", value=100).status_code, 200)
        out = self.add("resistor", value=200).get_json()
        self.assertEqual(out["components"]["R1"]["from"], "N0")
        self.assertEqual(out["components"]["R1"]["to"], "N1")
        self.assertEqual(out["components"]["R2"]["from"], "N1")
        self.assertEqual(out["last_node"], "N2")

    def test_self_loop_is_400_and_next_request_works(self):
        self.add("resistor", value=100)                       
        bad = self.add("resistor", to_node="N1")
        self.assertEqual(bad.status_code, 400)
        self.assertIn("cannot connect a node to itself", bad.get_json()["error"])
        bad = self.add("resistor", to_node="N1", value=100)  
        self.assertEqual(bad.status_code, 400)

        good = self.add("resistor", value=100)               
        self.assertEqual(good.status_code, 200)
        self.assertIn("R2", good.get_json()["components"])

    def test_negative_and_zero_values_are_400(self):
        for value in (-5, 0):
            res = self.add("resistor", value=value)
            self.assertEqual(res.status_code, 400, value)
            self.assertIn("greater than 0", res.get_json()["error"])

    def test_missing_value_is_400(self):
        res = self.add("resistor", from_node="new", to_node="new")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()["error"], "Missing field: value")

    def test_unknown_type_is_400(self):
        res = self.add("diode", value=1)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Unknown component type", res.get_json()["error"])

    def test_made_up_node_is_400(self):
        res = self.add("resistor", from_node="new", to_node="N99", value=1)
        self.assertEqual(res.status_code, 400)
        self.assertIn("N99", res.get_json()["error"])

    def test_failed_add_leaves_circuit_unchanged(self):
        self.add("resistor", value=100)
        self.add("resistor", value=200)
        before_data = server.circuit_data
        before_copy = {k: (list(v) if isinstance(v, list) else v) for k, v in before_data.items()}
        before_counters = dict(server.counters)

        res = self.add("resistor", from_node="N2", to_node="N2", value=100)
        self.assertEqual(res.status_code, 400)

        self.assertIs(server.circuit_data, before_data)      
        self.assertEqual(server.circuit_data, before_copy)
        self.assertEqual(server.counters, before_counters)    
        self.assertEqual(self.client.get("/state").get_json()["components"].keys(),
                         {"R1", "R2"})

    def test_components_sort_r1_r2_r10(self):
        for _ in range(10):
            self.add("resistor", value=100)
        ids = list(self.client.get("/state").get_json()["components"])
        self.assertEqual(ids[:3], ["R1", "R2", "R3"])
        self.assertEqual(ids[-1], "R10")
        self.assertEqual(ids.index("R2") < ids.index("R10"), True)

    def test_source_is_added_through_add_route(self):
        self.add("resistor", value=100)                       
        out = self.add("source", from_node="N0", to_node="N1", value=12).get_json()
        self.assertEqual(out["source"]["source_voltage"], 12.0)
        self.assertIn("V1", out["components"])

    def test_source_with_zero_volts_is_400(self):
        self.add("resistor", value=100)
        res = self.add("source", from_node="N0", to_node="N1", value=0)
        self.assertEqual(res.status_code, 400)

    def test_remove_and_unknown_remove(self):
        self.add("resistor", value=100)
        self.add("resistor", value=100)
        self.assertNotIn("R1", self.client.post("/remove/R1").get_json()["components"])
        res = self.client.post("/remove/R7")
        self.assertEqual(res.status_code, 404)
        self.assertIn("R7", res.get_json()["error"])
        self.assertEqual(self.client.get("/state").status_code, 200)

    def test_ground_must_be_an_existing_node(self):
        self.add("resistor", value=100)
        self.assertEqual(self.client.post("/ground", json={"node": "N5"}).status_code, 400)
        self.assertEqual(self.client.post("/ground", json={}).status_code, 400)
        ok = self.client.post("/ground", json={"node": "N1"})
        self.assertEqual(ok.get_json()["ground"], "N1")

    def test_removing_grounded_nodes_last_part_clears_ground(self):
        self.add("resistor", value=100)                       
        self.client.post("/ground", json={"node": "N1"})
        self.assertIsNone(self.client.post("/remove/R1").get_json()["ground"])

    def test_old_buttons_still_work(self):
        self.assertEqual(self.client.post("/add_resistor").status_code, 200)
        self.assertEqual(self.client.post("/add_capacitor").status_code, 200)
        out = self.client.post("/add_inductor").get_json()
        self.assertEqual(list(out["components"]), ["C1", "L1", "R1"])


if __name__ == "__main__":
    unittest.main()
