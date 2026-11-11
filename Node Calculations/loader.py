import json 
import components as cmps

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

    # Extract each dictionary one by one, which are within the "components" list
    def format_component(self):
        for comp in self.data.get("components", []):
            
            resistor_obj = cmps.resistor(
                comp["component_id"], 
                comp["component_type"], 
                comp["from_node"], 
                comp["to_node"], 
                comp["resistance"],
                {"series": [], "parallel": [],}
            )
            self.components[resistor_obj.id] = resistor_obj
            self.add_component_node(resistor_obj.from_node, resistor_obj)
            self.add_component_node(resistor_obj.to_node, resistor_obj)
        
    def format_source(self):
        
        source_obj = cmps.source(
            self.data["source"]["source_id"], 
            self.data["source"]["source_type"], 
            self.data["source"]["from_node"], 
            self.data["source"]["to_node"], 
            self.data["source"]["source_voltage"], 
            self.data["source"]["source_frequency"], 
            {"series": [], "parallel": [],}
        )
        self.components[source_obj.id] = source_obj
        self.add_component_node(source_obj.from_node, source_obj)
        self.add_component_node(source_obj.to_node, source_obj)
        
        
    def add_component_node(self, node_id, component):
        
        if node_id not in self.nodes:
            self.nodes[node_id] = cmps.node(node_id, 0)
        
        self.nodes[node_id].connected_components.append(component)
