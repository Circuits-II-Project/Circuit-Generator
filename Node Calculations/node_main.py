import loader as cl
import analyzer as al
import os

HERE = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    # Wipes the terminal screen completely clean before printing anything else
    os.system('cls' if os.name == 'nt' else 'clear')

    data = cl.load_from_file(os.path.join(HERE, "test_components.json"))
    load = cl.components_loader(data)
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
    
    