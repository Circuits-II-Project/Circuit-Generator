import json
import os
# Wipes the terminal screen completely clean before printing anything else
os.system('cls' if os.name == 'nt' else 'clear')

#Step 1: Read the information from the JSON file
# Storage -> Node -> Component

class component_manager:
    def __init__(self, id, type, from_node, to_node):
        self.id = id
        self.type = type
        self.from_node = from_node
        self.to_node = to_node


class node:
    def __init__(self, id, voltage):
        self.id = id
        self.voltage_at_node = voltage
        self.connected_components = []

class resistor(component_manager):
    def __init__(self, id, type, from_node, to_node, resistance):
        super().__init__(id, type, from_node, to_node)

        self.resistance = resistance
        
class source(component_manager):
    def __init__(self, id, type, from_node, to_node, voltage, frequency):
        super().__init__(id, type, from_node, to_node)
    
        self.frequency = frequency
        self.voltage = voltage
        
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
        
        
        
    def add_component_node(self, node_id, component):
        
        if node_id not in self.nodes:
            self.nodes[node_id] = node(node_id, 0)
        
        self.nodes[node_id].connected_components.append(component)

if __name__ == "__main__":
    s = components_loader("R2")
    o = s.components.items()
    for comp, obj in s.components.items():
        print(obj.to_node)
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