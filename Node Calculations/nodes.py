import json
import os
# Wipes the terminal screen completely clean before printing anything else
os.system('cls' if os.name == 'nt' else 'clear')

# Central class in which we call and create each component and node object and place the extracted JSON information into them.
class components_loader:
    def __init__(self):
        
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

# This Class will store the components at each node 
class node:
    def __init__(self, id, voltage):
        self.id = id
        self.voltage_at_node = voltage
        self.connected_components = []
        
    def __repr__(self):
        # Creates a clean text summary showing the node ID, voltage, and connected component IDs
        comp_ids = [c.id for c in self.connected_components]
        return f"Node(ID: {self.id}, Voltage: {self.voltage_at_node}V, Connected: {comp_ids})"
    
    def component_node_amount(self):
        print(len(self.connected_components))



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




# Analyze the connections between nodes for determining series or parallel
class connection_analyzer:
    def __init__(self, loaded_info):
        self.load = loaded_info
        
        self.node_components = {}
        self.node_temp_list = []
        self.label_component()
        
        
        
    def label_component(self):
    
        for node in self.load.nodes.values():
            print(f"Node {node.id} is Connected to:")
            #self.node_components[node.id]
            self.node_temp_list = []
            for comp in node.connected_components:
                
                print(f"Component ID: {comp.id}")
                self.node_temp_list.append(comp.id)
            self.node_components[node.id] = self.node_temp_list
           
        print(self.node_components)
    
    
    
    # def calculate_eqr_parallel(self, resistances):
    #     equivalent_resistance = 0
        
    #     # Add the resistors in fractions
    #     for resistor in resistances:
    #         equivalent_resistance += 1/resistor
        
    #     # Elevate the obtained resistance to the power of -1
    #     equivalent_resistance **= -1
    
    #     return equivalent_resistance

    # # Calculate the equivalent resistance of a series circouit
    # def calculate_eqr_series(self, resistances):
    #     equivalent_resistance = 0
        
    #     # Add the resistor values directly in a for loop
    #     for resistor in resistances:
    #         equivalent_resistance += resistor
        
    #     return equivalent_resistance

if __name__ == "__main__":
    load = components_loader()
    analyze = connection_analyzer(load)
    
    
    # resistances = []
    # for component_id, component in load.components.items():
    #     if isinstance(component, resistor):
    #         resistances.append(component.resistance)
    
    # equivalent_resistances = series_parallel()
    
    # total = equivalent_resistances.calculate_eqr_parallel(resistances)
    # print(total)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # o = s.nodes.items()
    # for node in s.nodes.values():
    #     print(node)
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