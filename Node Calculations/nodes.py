import json
import os
# Wipes the terminal screen completely clean before printing anything else
os.system('cls' if os.name == 'nt' else 'clear')

#Step 1: Read the information from the JSON file
# Storage -> Node -> Component

class component_manager:
    def __init__(self, id, type, value, frequency, from_node, to_node):
        self.id = id
        self.type = type
        self.value = value
        self.frequency = frequency
        self.from_node = from_node
        self.to_node = to_node





# class node:
#     def __init__(self, voltage_at_node, current_at_node, from_node, to_node, component_type, component_value):
#         self.voltage_at_node = 0
#         self.current_at_node = 0
#         self.from_node = " "
#         self.to_node = " "
#         self.component_type = " "
#         self.component_value = 0

class resistor(component_manager):
    def __init__(self):
        super().innit__()
        self.component_id = None
        self.component_type = None
        self.component_value = None
        self.from_node = None
        self.to_node = None

class source(component_manager):
    def __init__(self):
        self.source_id = None
        self.source_type = None
        self.source_voltage = None
        self.source_frequency = None
        self.source_from_node = None
        self.source_to_node = None
        
class components_loader:
    def __init__(self, id):
        
        self.read_info() 
        
        self.component_id = id
        self.component_type = None
        self.component_value = None
        self.from_node = None
        self.to_node = None
        
        self.source_id = None
        self.source_type = None
        self.source_voltage = None
        self.source_frequency = None
        self.source_from_node = None
        self.source_to_node = None
    
        self.format_component()
        self.format_source()
        
        
    
    def read_info(self):
        with open("test_components.json", 'r') as file:
            self.data = json.load(file)
    
    # Extract each dictionary one by one, which are within the "components" list
    def format_component(self):
        for comp in self.data.get("components", []):
            if comp["component_id"] == self.component_id:
                self.component_id = comp["component_id"]
                self.component_type = comp["component_type"]
                self.component_value = comp["resistance"]
                self.from_node = comp["from_node"]
                self.to_node = comp["to_node"]
        
    def format_source(self):
        self.source_id = self.data["source"]["source_id"]
        self.source_type = self.data["source"]["source_type"]
        self.source_voltage = self.data["source"]["source_voltage"]
        self.source_frequency = self.data["source"]["source_frequency"]
        self.source_from_node = self.data["source"]["from_node"]
        self.source_to_node = self.data["source"]["to_node"]

      

if __name__ == "__main__":
   s = components_loader("R2")
   
