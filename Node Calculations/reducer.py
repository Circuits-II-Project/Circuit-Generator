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
        # Try parallel reduction first
        if self.calculate_parallel_resistors():
            return
            
        # Otherwise, try series reduction
        if self.calculate_series_resistors():
            return
            
    def calculate_parallel_resistors(self):
        for obj in self.resistor_info:
            if obj["id"] in self.checked_resistors:
                continue
                
            if obj["parallel_partners"]:
                # Include BOTH the base object and its parallel partners
                group_ids = [obj["id"]] + obj["parallel_partners"]
                
                # Mark all as checked
                for pid in obj["parallel_partners"]:
                    self.checked_resistors.append(pid)
                self.checked_resistors.append(obj["id"])
                
                # Gather matching resistor info dictionaries
                group_objs = [r for r in self.resistor_info if r["id"] in group_ids]
                
                # Calculate equivalent resistor
                eq_res = cmps.resistor.calculate_eqr_parallel(group_objs)
                
                # Remove old components and add the new equivalent one
                for r_id in group_ids:
                    self.loaded_info.remove_component(r_id)
                self.loaded_info.add_component(eq_res)
                
                return True # Perform one reduction and let the while loop re-analyze
        return False
       

    
    def calculate_series_resistors(self):
        for obj in self.resistor_info:
            if obj["id"] in self.checked_resistors:
                continue
                
            if obj["series_partners"]:
                # Include BOTH the base object and its series partners
                group_ids = [obj["id"]] + obj["series_partners"]
                
                # Mark all as checked
                for pid in obj["series_partners"]:
                    self.checked_resistors.append(pid)
                self.checked_resistors.append(obj["id"])
                
                # Gather matching resistor info dictionaries
                group_objs = [r for r in self.resistor_info if r["id"] in group_ids]
                
                # Calculate equivalent resistor
                eq_res = cmps.resistor.calculate_eqr_series(group_objs)
                
                # Remove old components and add the new equivalent one
                for r_id in group_ids:
                    self.loaded_info.remove_component(r_id)
                self.loaded_info.add_component(eq_res)
                
                return True # Perform one reduction and let the while loop re-analyze
        return False
        
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

    
    