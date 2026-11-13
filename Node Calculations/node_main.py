import loader as cl
import analyzer as al
import calculations as calc
import os

# Wipes the terminal screen completely clean before printing anything else
os.system('cls' if os.name == 'nt' else 'clear')
if __name__ == "__main__":
    load = cl.components_loader()
    al.connection_analyzer(load)
    calc.node_calculations(load)
    
    
    
    
    # print("=" * 50)
    # print("               CIRCUIT NODES              ")
    # print("=" * 50)
    
    # # Loop through all saved nodes
    # for node_id, node_obj in load.nodes.items():
    #     print(f"  -> {node_obj}")
        
    # print("\n" + "=" * 50)
    # print("         SAVED COMPONENTS & TAGS          ")
    # print("=" * 50)
    
    # # Loop through all saved components
    # for comp_id, obj in load.components.items():
    #     print(f"  Component ID : {obj.id}")
    #     print(f"  Type         : {obj.type}")
    #     print(f"  Connections  : Node {obj.from_node} -> Node {obj.to_node}")
        
    #     # Check for resistor-specific attribute using loop-safe checks
    #     if hasattr(obj, "resistance"):
    #         print(f"  Resistance   : {obj.resistance} Ω")
            
    #     # Check for source-specific attributes
    #     if hasattr(obj, "voltage"):
    #         print(f"  Voltage      : {obj.voltage}V")
    #         print(f"  Frequency    : {obj.frequency}Hz")
            
    #     # Extract tag partner IDs using list comprehensions inside the loop
    #     series_partners = [partner.id for partner in obj.tag["series"]]
    #     parallel_partners = [partner.id for partner in obj.tag["parallel"]]
        
    #     print(f"  Series Tags  : {series_partners if series_partners else 'None'}")
    #     print(f"  Parallel Tags: {parallel_partners if parallel_partners else 'None'}")
    #     print("-" * 50)
    
    