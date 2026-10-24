import json


#Step 1: Read the information from the JSON file

class node:
    def __init__(self, voltage_at_node, current_at_node, from_node, to_node, component_type, component_value):
        self.voltage_at_node = 0
        self.current_at_node = 0
        self.from_node = " "
        self.to_node = " "
        self.component_type = " "
        self.component_value = 0


class storage(node):
    def __init__(self):
        self.voltage_at_node = 0
        self.current_at_node = 0
        self.from_node = " "
        self.to_node = " "
        self.component_type = " "
        self.component_value = 0
        
        super().__init__(self, self.voltage_at_node, self.current_at_node, self.from_node, self.to_node, self.component_type, self.component_value)
        

    def read_info(self):
        with open("test_components.json", 'r') as file:
            self.received_information = json.load(file)
        
        1
    
        

class input_test:
    def __init__(self, input_id, input_name, input_type, input_value):
        self.input_id = input_id
        self.input_name = input_name
        self.input_type = input_type
        self.input_value = input_value    
        
if __name__ == "__main__":
   storage().read_info()
  