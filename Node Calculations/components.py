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
    
    @classmethod
    def calculate_eqr_parallel(cls, parallel_resistors):
        equivalent_resistance = 0

        # Add the resistors in fractions
        for current_res in parallel_resistors:
            #print(resistor["resistance"])
            equivalent_resistance += 1/current_res["resistance"]
        
        # Elevate the obtained resistance to the power of -1
        equivalent_resistance **= -1
        
        name_id = "parallel_" + "_".join([res["id"] for res in parallel_resistors])   
        eq_parallel_resistors = resistor(
                            id=name_id,
                            type="resistor",
                            from_node=parallel_resistors[0]["from_node"],
                            to_node=parallel_resistors[0]["to_node"],
                            resistance=equivalent_resistance,
                            tag={"series": [], "parallel": [],}
                        )
        return eq_parallel_resistors
    
    @classmethod
    def calculate_eqr_series(cls, series_resistors):
        equivalent_resistance = 0
        all_nodes = []
        
        # Sum resistance and collect all connected nodes
        for current_res in series_resistors:
            equivalent_resistance += current_res["resistance"] 
            all_nodes.append(current_res["from_node"])
            all_nodes.append(current_res["to_node"])
        
        # Count how many times each node appears
        node_counts = {}
        for n in all_nodes:
            node_counts[n] = node_counts.get(n, 0) + 1
            
        # Outer nodes appear only once (endpoints), internal nodes appear twice (shared)
        outer_nodes = [n for n, count in node_counts.items() if count == 1]
        
        
        name_id = "series_" + "_".join([res["id"] for res in series_resistors])   
        eq_series_resistors = resistor(
                            id=name_id,
                            type="resistor",
                            from_node=outer_nodes[0],
                            to_node=outer_nodes[1],
                            resistance=equivalent_resistance,
                            tag={"series": [], "parallel": [],}
                        )
        
        
        return eq_series_resistors
    
# This Class will store the information of the voltage source.
class source(component_manager):
    def __init__(self, id, type, from_node, to_node, voltage, frequency, tag):
        super().__init__(id, type, from_node, to_node, tag)
    
        self.frequency = frequency
        self.voltage = voltage
