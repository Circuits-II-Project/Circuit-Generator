import json 
import components as cmps

# component_type -> class to create, JSON field that holds its value
# To support a new component add one line here.

COMPONENT_TYPES = {
    "resistor": (cmps.resistor, "resistance"),
    "capacitor": (cmps.capacitor, "capacitance"),
    "inductor": (cmps.inductor, "inductance"),
}

# Reads a circuit JSON file and returns its contents as a dict (outside the class on purpose).
def load_from_file(path: str) -> dict:
    with open(path,'r') as file:
        return json.load(file)

# Central class in which we create each component and node object from the circuit data (a dict).
# The data can come from a file (load_from_file) or directly from the GUI in memory.
class components_loader:
    def __init__(self,data: dict):

        self.data = data
        self.nodes = {}
        self.components = {}
        self.format_component()
        self.format_source()

    # Extract each dictionary from the components list and create the right class for its type
    def format_component(self):
        for comp in self.data.get("components", []):

            comp_type = comp["component_type"]
            if comp_type not in COMPONENT_TYPES:
                raise ValueError(f"Unknown component_type '{comp_type}' in {comp['component_id']}")

            cls, value_field = COMPONENT_TYPES[comp_type]

            comp_obj = cls(
                comp["component_id"],
                comp_type,
                comp["from_node"],
                comp["to_node"],
                comp[value_field],
                {"series": [], "parallel": []}
            )            

            self.components[comp_obj.id] = comp_obj
            self.add_component_node(comp_obj.from_node, comp_obj)
            self.add_component_node(comp_obj.to_node, comp_obj)
        
    def format_source(self):
        #User may not have added any sources yet, so it is optional

        if "source" not in self.data or self.data["source"] is None:
            return
        
        src = self.data["source"]
        source_obj = cmps.source(
            src["source_id"],
            src["source_type"],
            src["from_node"],
            src["to_node"],
            src["source_voltage"],
            src.get("source_frequency"), #dc may not have one
            {"series": [], "parallel": []}
        )
        self.components[source_obj.id] = source_obj
        self.add_component_node(source_obj.from_node, source_obj)
        self.add_component_node(source_obj.to_node, source_obj)
        
        
    def add_component_node(self, node_id, component):
        
        if node_id not in self.nodes:
            self.nodes[node_id] = cmps.node(node_id, 0)
        
        self.nodes[node_id].connected_components.append(component)
