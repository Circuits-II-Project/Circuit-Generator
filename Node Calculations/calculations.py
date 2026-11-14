# Class for calculating the needed data at each node and at each component.
class calculate_components:
    def __init__(self, loaded_info):
        self.resistor_info = []
        self.loaded_info = loaded_info
        self.store_resistors()
        self.calculate_resistors()
    
    
    def calculate_resistors(self):
        for key in self.resistor_info: 
            print(key)
    
    
    def store_resistors(self):
                    
        # Loop through all components stored in the loader object
        for comp_id, obj in self.loaded_info.components.items():
            # Check if the component type is a resistor
            if obj.type == "resistor":
                
                # Gather its attributes into a structured dictionary
                res_info = {
                    "id": obj.id,
                    "resistance": obj.resistance,
                    "from_node": obj.from_node,
                    "to_node": obj.to_node,
                    "series_partners": [partner.id for partner in obj.tag["series"]],
                    "parallel_partners": [partner.id for partner in obj.tag["parallel"]]
                }
            
            # Append the dictionary to your collection list
            self.resistor_info.append(res_info)

        # Example: Print the stored records to verify
        for r in self.resistor_info:
            print(r)
    
    
    def calculate_eqr_parallel(self, resistances):
        equivalent_resistance = 0
        
        # Add the resistors in fractions
        for resistor in resistances:
            equivalent_resistance += 1/resistor
        
        # Elevate the obtained resistance to the power of -1
        equivalent_resistance **= -1
        
        return equivalent_resistance

    # Calculate the equivalent resistance of a series circouit
    def calculate_eqr_series(self, resistances):
        equivalent_resistance = 0
        
        # Add the resistor values directly in a for loop
        for resistor in resistances:
            equivalent_resistance += resistor
        
        return equivalent_resistance