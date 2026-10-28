import loader as cl
import analyzer as al
import os

# Wipes the terminal screen completely clean before printing anything else
os.system('cls' if os.name == 'nt' else 'clear')
if __name__ == "__main__":
    load = cl.components_loader()
    analyze = al.connection_analyzer(load)
    
   # components = analyze.node_components
    #print(components)
    
    for id, component in load.components.items():
        print(id, component.tag)

        for key, connection in component.tag.items():
            print(connection)
            
            for other in connection:
                print(other.id)
                pass
                #print(f"ID: {id} | Component in series: {other.id} & Component in parallel: {other.id}")
    
    