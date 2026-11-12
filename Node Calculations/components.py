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

#This class will store all formulas and information to a capacitor component
class capacitor(component_manager):
    def __init__(self, id, type, from_node, to_node, capacitance, tag):
        super().__init__(id, type, from_node, to_node, tag)
        self.capacitance = capacitance

class inductor(component_manager):
    def __init__(self, id, type, from_node, to_node, inductance, tag):
        super().__init__(id, type, from_node, to_node, tag)
        self.inductance = inductance

# This Class will store the information of the voltage source.
class source(component_manager):
    def __init__(self, id, type, from_node, to_node, voltage, frequency, tag):
        super().__init__(id, type, from_node, to_node, tag)
    
        self.frequency = frequency
        self.voltage = voltage
