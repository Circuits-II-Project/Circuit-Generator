import json
import os
# Wipes the terminal screen completely clean before printing anything else
os.system('cls' if os.name == 'nt' else 'clear')

class components_loader:
    def __init__(self, id):
        self.component_id = id
        self.nodes = {}
        self.components = {}
        self.read_info() 
        self.format_component()
        self.format_source()
        
        
    
    def read_info(self):
        with open("test_components.json", 'r') as file:
            self.data = json.load(file)
    
    # Extract each dictionary one by one, which are within the "components" list
    def format_component(self):
        for comp in self.data.get("components", []):
            if comp["component_id"] == self.component_id:
                resistor_obj = resistor(
                    comp["component_id"], 
                    comp["component_type"], 
                    comp["from_node"], 
                    comp["to_node"], 
                    comp["resistance"]
                )
                self.components[resistor_obj.id] = resistor_obj
                self.add_component_node(resistor_obj.from_node, resistor_obj)
                self.add_component_node(resistor_obj.to_node, resistor_obj)
        
    def format_source(self):
        
        source_obj = source(
            self.data["source"]["source_id"], 
            self.data["source"]["source_type"], 
            self.data["source"]["from_node"], 
            self.data["source"]["to_node"], 
            self.data["source"]["source_voltage"], 
            self.data["source"]["source_frequency"]
        )
        self.components[source_obj.id] = source_obj
        self.add_component_node(source_obj.from_node, source_obj)
        self.add_component_node(source_obj.to_node, source_obj)
        
        
    def add_component_node(self, node_id, component):
        
        if node_id not in self.nodes:
            self.nodes[node_id] = node(node_id, 0)
        
        self.nodes[node_id].connected_components.append(component)

# Class for storing the general information of the subclasses. This class acts as a Parent or Superclass, which does not need to be instantiated.
class component_manager:
    def __init__(self, id, type, from_node, to_node):
        self.id = id
        self.type = type
        self.from_node = from_node
        self.to_node = to_node

# This Class will store the components at each node with their `from` and `to` node connections.
class node:
    def __init__(self, id, voltage):
        self.id = id
        self.voltage_at_node = voltage
        self.connected_components = []
        
    def __repr__(self):
        # Creates a clean text summary showing the node ID, voltage, and connected component IDs
        comp_ids = [c.id for c in self.connected_components]
        return f"Node(ID: {self.id}, Voltage: {self.voltage_at_node}V, Connected: {comp_ids})"
    
# This class will store are formulas and information related to a resistor component.
class resistor(component_manager):
    def __init__(self, id, type, from_node, to_node, resistance):
        super().__init__(id, type, from_node, to_node)

        self.resistance = resistance

# This Class will store the information of the voltage source.
class source(component_manager):
    def __init__(self, id, type, from_node, to_node, voltage, frequency):
        super().__init__(id, type, from_node, to_node)
    
        self.frequency = frequency
        self.voltage = voltage
        

if __name__ == "__main__":
    s = components_loader("R2")
    o = s.nodes.items()
    for node in s.nodes.values():
        print(node)
    # print("--- SAVED COMPONENTS ---")
    # for comp_id, obj in s.components.items():
    #     print(f"Component ID : {obj.id}")
    #     print(f"Type         : {obj.type}")
    #     print(f"Connected    : {obj.from_node} -> {obj.to_node}")
        
    #     # Check for resistor-specific attribute
    #     if hasattr(obj, "resistance"):
    #         print(f"Resistance   : {obj.resistance} ohms")
            
    #     # Check for source-specific attribute
    #     if hasattr(obj, "voltage"):
    #         print(f"Voltage      : {obj.voltage}V")
    #         print(f"Frequency    : {obj.frequency}Hz")
            
    #     print("-" * 25)