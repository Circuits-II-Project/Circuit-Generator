

class circuit_solver:
    def __init__(self, loaded_info):
        
        self.loaded_info = loaded_info
        self.reduction_history = self.loaded_info.reduction_history
        self.complete_data = self.loaded_info.complete_data
    
        
        self.total_voltage = None
        self.source = None
        self.eq_resistor = None
        self.eq_resistance = None
        self.total_current = None
        self.components_current = {}
        self.components_voltage = {}
    
        self.obtain_values()
        self.reverse_solve()
        self.print_results()
        
   
    
    # Method for retrieving the voltage and equivalent resitance of the whole circuit
    def obtain_values(self):
        for id, obj in self.loaded_info.components.items():
            
            if obj.type == "DC":
               self.source = obj
               self.total_voltage = obj.voltage
            
            if obj.type == "resistor":
                self.eq_resistor = obj
                self.eq_resistance = obj.resistance
            
        if not self.total_voltage or not self.eq_resistor:
            print("Error: Could not find source or equivalent resistor for solving.")
        else:
            self.calculate_current()
        
       
            
    def calculate_current(self):
        self.total_current = self.total_voltage / self.eq_resistance
        
    def reverse_solve(self):
        # Assign total current and voltage to the final equivalent component
        top_step = self.reduction_history[-1]
        top_parent_id = top_step["parent_id"]
        
        # Assign total current and voltage to the final equivalent component
        self.components_current[top_parent_id] = self.total_current
        self.components_voltage[top_parent_id] = self.total_voltage
        
        # Build a resistance map from both the history and base components
        resistance_map = {step["parent_id"]: step["resistance"] for step in self.reduction_history}
        
       
        
        for cid, obj in self.complete_data.items(): # Adjust if your loader uses .components
            if hasattr(obj, 'resistance') and obj.resistance is not None:
                resistance_map[cid] = obj.resistance
        
        
        #print(resistance_map)
        for step in reversed(self.reduction_history):
            parent_id = step["parent_id"]
            reduction_type = step["type"]
            children_ids = step["children_ids"]
        
            
            parent_current = self.components_current.get(parent_id, self.total_current)
            parent_voltage = self.components_voltage.get(parent_id, self.total_voltage)
            
            #print(parent_voltage)
           
            
            if reduction_type == "series":
            
                for child_id in children_ids:
                    
                    self.components_current[child_id] = parent_current
                    
                    child_resistance = resistance_map.get(child_id)
                    
                    if child_resistance is not None:
                        
                        child_voltage = parent_current * child_resistance
                        self.components_voltage[child_id] = child_voltage
                        
                        #print(parent_id, child_voltage)
            
            elif reduction_type == "parallel":
                
                for child_id in children_ids:
                    
                    self.components_voltage[child_id] = parent_voltage

                    child_resistance = resistance_map.get(child_id)
                    if child_resistance and child_resistance > 0:
                        #print(parent_voltage)
                        child_current = parent_voltage/child_resistance
                        self.components_current[child_id] = child_current
                       
                        
                        
            #print(f"voltage: {self.components_voltage}")
           # print(f"current:{self.components_current}")
        #print(self.components_current)
            # # Check what reduction type was used
            # if reduction_type == "series":
                
            #     for child_id in children_ids: 
            #         # Current is the same for all series children
            #         self.components_current[child_id] = parent_current
                    
            #         child_obj = self.complete_data.get(child_id)
                    
            #         if child_obj:
            #             # Calculate the actual voltage drop for this specific child!
            #             child_voltage = parent_current * child_obj.resistance
            #             self.components_voltage[child_id] = child_voltage
            #             print(parent_id, child_voltage)
            
            # # Check if the reduction type is parallel
            # elif reduction_type == "parallel":
               
            #     # In parallel: Voltage is the same for all children. Current splits.
            #     for child_id in children_ids:
                    
            #         # Loop through each child resistor and assign the parent voltage to it
            #         self.components_voltage[child_id] = parent_voltage
                    
            #         # Extract from the complete data's list the object of the resistor
            #         child_obj = self.complete_data.get(child_id)
                    
            #         # Assign the current to the child resistor in the dictionary
            #         if child_obj and child_obj.resistance > 0:
            #             self.components_current[child_id] = parent_voltage / child_obj.resistance
            #             print(parent_id, parent_voltage)
        #print(self.reduction_history)
        #print(self.components_voltage)
    def print_results(self):
        
        print("\n" + "=" * 60)
        print("           CIRCUIT SOLVER: VOLTAGES & CURRENTS          ")
        print("=" * 60)
        print(f"{'Component ID':<15} | {'Voltage (V)':<15} | {'Current (A)'}")
        print("-" * 60)
        
        # Get all unique component IDs from both dictionaries
        all_ids = sorted(list(set(list(self.components_voltage.keys()) + list(self.components_current.keys()))))
        
        for cid in all_ids:
            voltage = self.components_voltage.get(cid, 0.0)
            current = self.components_current.get(cid, 0.0)
            print(f"{cid:<15} | {voltage:<15.2f} | {current:.4f} A")
            
        print("=" * 60)
                
        
       