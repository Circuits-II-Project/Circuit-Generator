import os
import sys
import unittest

# Allow importing loader/analyzer from "Node Calculations"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, "..", "Node Calculations"))

import loader as cl
import analyzer as al


# Helpers to build test data quickly
def resistor(rid, a, b, r=100.0):
    return {"component_id": rid, "component_type": "resistor",
            "from_node": a, "to_node": b, "resistance": r}

SOURCE = {"source_id": "V1", "source_type": "DC", "source_voltage": 12.0,
          "source_frequency": None, "from_node": "A", "to_node": "C"}


class LoaderTests(unittest.TestCase):

    def test_accepts_dict_in_memory(self):        # change #1
        data = {"source": SOURCE, "components": [resistor("R1", "A", "B")]}
        load = cl.components_loader(data)
        self.assertIn("R1", load.components)
        self.assertIn("V1", load.components)

    def test_creates_nodes(self):
        data = {"source": SOURCE, "components": [resistor("R1", "A", "B")]}
        load = cl.components_loader(data)
        self.assertEqual(set(load.nodes), {"A", "B", "C"})

    def test_without_source_does_not_crash(self):  # change #2
        data = {"components": [resistor("R1", "A", "B")]}
        load = cl.components_loader(data)
        self.assertNotIn("V1", load.components)

    def test_empty_circuit(self):                  # GUI with nothing added yet
        load = cl.components_loader({})
        self.assertEqual(load.components, {})

    def test_load_from_file(self):
        path = os.path.join(HERE, "..", "Node Calculations", "test_components.json")
        data = cl.load_from_file(path)
        self.assertEqual(len(data["components"]), 4)


class AnalyzerTests(unittest.TestCase):

    def test_parallel(self):
        data = {"components": [resistor("R1", "A", "B"), resistor("R2", "A", "B")]}
        load = cl.components_loader(data)
        al.connection_analyzer(load)
        self.assertEqual([c.id for c in load.components["R1"].tag["parallel"]], ["R2"])

    def test_series(self):
        data = {"components": [resistor("R1", "A", "B"), resistor("R2", "B", "C")]}
        load = cl.components_loader(data)
        al.connection_analyzer(load)
        self.assertEqual([c.id for c in load.components["R1"].tag["series"]], ["R2"])

    def test_creates_capacitor_and_inductor(self):
        data = {"components": [
            {"component_id": "C1", "component_type": "capacitor", "from_node": "A", "to_node": "B", "capacitance": 1e-6},
            {"component_id": "L1", "component_type": "inductor", "from_node": "B", "to_node": "C", "inductance": 0.01},
        ]}
        load = cl.components_loader(data)
        self.assertEqual(load.components["C1"].capacitance, 1e-6)
        self.assertEqual(load.components["L1"].inductance, 0.01)

    def test_unkown_type_raises(self):
        data = {"components": [{"component_id": "X1", "component_type": "diode",
                                "from_node": "A", "to_node": "B"}]}
        with self.assertRaises(ValueError):
            cl.components_loader(data)

    def test_rebuild_drops_stale_series_tag(self):
        data = {"components": [
            {"component_id": "R1", "component_type": "resistor", "from_node": "A", "to_node": "B", "resistance": 100},
            {"component_id": "R2", "component_type": "resistor", "from_node": "B", "to_node": "C", "resistance": 200},
        ]}
        load = cl.components_loader(data)
        al.connection_analyzer(load)
        self.assertEqual([c.id for c in load.components["R1"].tag["series"]], ["R2"])

        #Node b goes from 2 to 3 components, so R1 and R2 are no longer in series
        data["components"].append({"component_id": "R3", "component_type": "resistor", "from_node": "B", "to_node": "D", "resistance": 300})
        load = cl.components_loader(data)
        al.connection_analyzer(load)
        self.assertEqual(load.components["R1"].tag["series"], [])

    def test_parallel_pair_is_not_series(self):
        data = {"components": [resistor("R1", "A", "B"), resistor("R2", "A", "B")]}
        load = cl.components_loader(data)
        al.connection_analyzer(load)
        self.assertEqual(load.components["R1"].tag["series"], [])

    def test_self_loop_raises(self):
        with self.assertRaises(ValueError):
            cl.components_loader({"components": [resistor("R1", "A", "A")]})

    def test_series_groups(self):
        data = {"components": [resistor("R1", "A", "B"), resistor("R2", "B", "C"), resistor("R3", "C", "D")]}
        load = cl.components_loader(data)
        self.assertEqual(al.connection_analyzer(load).series_groups(), [["R1", "R2", "R3"]])


if __name__ == "__main__":
    unittest.main()
