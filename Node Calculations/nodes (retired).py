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
                comp["resistance"],
                {"series": [], "parallel": [],}
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
            self.data["source"]["source_frequency"], 
            {"series": [], "parallel": [],}
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
    def __init__(self, id, type, from_node, to_node, tag):
        self.id = id
        self.type = type
        self.from_node = from_node
        self.to_node = to_node
        self.tag = tag

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

# This class will store all formulas and information related to a resistor component.
class resistor(component_manager):
    def __init__(self, id, type, from_node, to_node, resistance, tag):
        super().__init__(id, type, from_node, to_node, tag)

        self.resistance = resistance

# This Class will store the information of the voltage source.
class source(component_manager):
    def __init__(self, id, type, from_node, to_node, voltage, frequency, tag):
        super().__init__(id, type, from_node, to_node, tag)
    
        self.frequency = frequency
        self.voltage = voltage

# Analyze the connections between nodes for determining series or parallel
class connection_analyzer:
    def __init__(self, loaded_info):
        
        self.load = loaded_info
        
        self.node_components = {}
        self.node_temp_list = []
        self.parallel_temp_list = []
        self.series_temp_list = []
        self.separate_components()
        self.tag_series()
        self.tag_parallel()
        
        
    def separate_components(self):
    
        for node in self.load.nodes.values():
            self.node_temp_list = [] # Empty the list for new values
            
            for comp in node.connected_components:
                self.node_temp_list.append(comp) # Append the component's id to the temporary list
                
                
            self.node_components[node.id] = self.node_temp_list # Assignt the created list into the general dictionary
    
    def tag_series(self):
        
        for node, comp in self.node_components.items():    
            
            # Check if the amount of components in a node is exactly 2    
            if len(comp) == 2:
                
                # Assign the components to temp variables
                c1 = comp[0] 
                c2 = comp[1]
                
                # Check that the component is not already registered. If its not, then we save it
                if c1 not in c2.tag["series"]:
                    c1.tag["series"].append(c2)
                
                if c2 not in c1.tag["series"]:
                    c2.tag["series"].append(c1)
                    
                #print(f"Series Components: {comp} | node: {node}") # Prints the components that are connected to the same node.
                
    
    def tag_parallel(self):
        
        # Looping through the nodes
        for node, comp in self.node_components.items():
        
            # Looping through the components
            for sub_node, sub_comp in self.node_components.items():
               
                # Check that we are not checking the same nodes in both loops, so that we do not compare the same component list
                if node != sub_node:
                    overlap = set(comp) & set(sub_comp) # Save the components that show up in both lists
                    
                    if len(overlap) >= 2: # Check that there are 2 or more components at the node
                        
                        #print(f"Components are in parallel: {overlap}")
                        
                        # Loop through the components in the overlap
                        for item in overlap:
                            # Loop through all components and check that the current component is not equal to the item we are checking in the overlap
                            # Ensures that each components saves the parallel components to it and NOT itself
                            parallel_comp = [other for other in overlap if other != item] 
                            item.tag["parallel"] = parallel_comp
                            
                            #print(item.tag)
                        # comp.tag["parallel"] = overlap
       
# Here we can use it to output values for checking (for the future)
class testing:
    pass
    
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