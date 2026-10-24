# Node Logic

- For the node logic, there are main areas that need to be taken into account to ensure that it works correctly. 
- For determining what noedes yto use, we will have a general list of the notes and a temporary node, which will let us identify by separate each are of a component. We
  will also have temporary variables for the voltage and current (or any other needed). For this:

## Step 1: Register Ground
- The program will read the JSON file and identify the nodes and branch where the component is placed.

## Step 2: Component Info
- Receive the information regarding the component about its two connecting nodes.
- Temporary variables will be assigned for the incoming current and voltage going through the component.

## Step 3: Branch and Node Analysis
- Check if components are in series or parallel
  - This may be done by identifying how many components or branches stem from a specific branch
  - If its only 1, then its series. If there is more than 1, then its parallel.
- Obtain the current across the branches in case of parallel, so that they can be correctly divided.
- When the current is determined, the JSON file must be updated and this information must be saved.

---
# Borrador
1. Receive the information of the component yet to be analyzed.
2. Receive the two nodes at each of the component.
3. Give those nodes temporary names for the calculations
4. Use the temporary current and voltage variables for calculating the value we want.

- Have a dictionary for the current in each branch.
- Check if the first node of the component is registered in another component, to ensure that the current is divided or added, depending on series or parallel.
- For the ground node, the whole circuit is first registered to check where the ground node is placed. This will let us pinpoint in between which nodes and in which branch is placed.
  - Scan the JSON file for this specific component, so we can extract the node or branch where it is placed.
---


# Steps taken to create code

- I will use a generated JSON file for testing and as a guide for the program, ensuring that the program does not depend on the JSON file directly.
- I will make use of a class for controlling the node information

## Classes

### Nodes
- There will be a class created each time that a node is analyzed, each with its own information about the votlage, current, component, and id
- Currently, we have 5 classes:
  - resistor
  - source
  - component_loader
  - node
  - component_manager
- The information that is saved about each component is saved between these classes.
- The classes are correctly structured for adding mroe components without causing issues (inductors and capacitors).
  
*resistor Class*
- It will hold the functions for calculating any related value of voltage or current with the resistor
- It will inheriate from the component_manager Class to store information as well

*node Class*
- It will keep track of the components on the circuit, primarely the nodes that are connected to those saved
  components

*source Class*
- Similary to the resistor Class, but with the information of the voltage source of the circuit. It will also inheriate
  from the component_manager Class.

*component_loader Class*
- The main control of all the classes. Here we extract the information from the JSON file and create the class objects of each component in the
  circuit and the node Class objects for identifying the position of each component.

*component_manager Class*
- Superclass from which the ressitor and node Class inheriate variables, since there is a direct connection and similar values between the components