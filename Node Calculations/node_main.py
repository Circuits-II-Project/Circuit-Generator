import loader as cl
import analyzer as al
import os

# Wipes the terminal screen completely clean before printing anything else
os.system('cls' if os.name == 'nt' else 'clear')
if __name__ == "__main__":
    load = cl.components_loader()
    analyze = al.connection_analyzer(load)
    

    
    
    
    