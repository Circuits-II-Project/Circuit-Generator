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
  