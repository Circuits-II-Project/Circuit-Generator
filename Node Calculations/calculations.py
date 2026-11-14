from modulefinder import test

import components as cmps

# Class for calculating the needed data at each node and at each component.
class calculate_components:
    def __init__(self, loaded_info):
        self.resistor_info = []
        self.resistors = []
        self.checked_resistors = []
        self.loaded_info = loaded_info
        self.store_resistors()
        self.reduction_process()
        #self.calculate_series_resistors()
    
    
    def reduction_process(self):
        parallel_available = any(len(obj["parallel_partners"]) > 0 for obj in self.resistor_info)
        
        if parallel_available:
            self.calculate_parallel_resistors()
        
        series_available = any(len(obj["series_partners"]) > 0 for obj in self.resistor_info)
        
        if series_available:
            self.calculate_series_resistors()
            
    def calculate_parallel_resistors(self):
        
        # Retrieve a resistor
        for obj in self.resistor_info:
              
            # Loop through the parallel partners of the resistor
            for partner in obj["parallel_partners"]:
                
                # If the partner is not on the checked list of resistrs, we add it
                if partner not in self.checked_resistors:
                    
                    self.checked_resistors.append(partner)
                    
                    # Loop through the resistor objects again
                    for selected_obj in self.resistor_info:
                        
                        # If the id of the resistor is the same as the partner, we append it to the resistor list
                        if selected_obj["id"] == partner:
                            
                            self.resistors.append(selected_obj)
        #print(self.checked_resistors)
        #print(self.calculate_eqr_parallel(self.resistors))
        test = cmps.resistor.calculate_eqr_parallel(self.resistors)
        
        #print(test.resistance)
        
        # 1. Collect the IDs of the resistors you just collapsed
        collapsed_ids = [r["id"] for r in self.resistors]

        #print(collapsed_ids)

        #print(self.loaded_info.components)
        for ids in collapsed_ids:
            self.loaded_info.remove_component(ids)
            
        self.loaded_info.add_component(test)
        #print(self.loaded_info.components)
        
        self.resistors = []
        self.checked_resistors = []
       

    
    def calculate_series_resistors(self):
        # Retrieve a resistor
        for obj in self.resistor_info:
                
            # Loop through the parallel partners of the resistor
            for partner in obj["series_partners"]:
                
                # If the partner is not on the checked list of resistrs, we add it
                if partner not in self.checked_resistors:
                    
                    self.checked_resistors.append(partner)
                    
                    # Loop through the resistor objects again
                    for selected_obj in self.resistor_info:
                        
                        # If the id of the resistor is the same as the partner, we append it to the resistor list
                        if selected_obj["id"] == partner:
                        
                            self.resistors.append(selected_obj)
        #print(self.checked_resistors)
        #print(self.calculate_eqr_parallel(self.resistors))
        test = cmps.resistor.calculate_eqr_parallel(self.resistors)
        
        #print(test.resistance)
        
        # 1. Collect the IDs of the resistors you just collapsed
        collapsed_ids = [r["id"] for r in self.resistors]

        #print(collapsed_ids)

        #print(self.loaded_info.components)
        for ids in collapsed_ids:
            self.loaded_info.remove_component(ids)
            
        self.loaded_info.add_component(test)
        #print(self.loaded_info.components)
        
        self.resistors = []
        self.checked_resistors = []
        
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

        # # Example: Print the stored records to verify
        # for r in self.resistor_info:
        #     print(r)
    
    
    def calculate_eqr_parallel(self, resistances):
        equivalent_resistance = 0
        
        # Add the resistors in fractions
        for resistor in resistances:
            #print(resistor["resistance"])
            equivalent_resistance += 1/resistor["resistance"]
        
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