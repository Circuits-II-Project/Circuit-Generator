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
- It will keep track of the components on the circuit, primarely the nodes that are connected to the saved components. It will save the `from` and `to` 
  nodes of each component, each one correctly identified to their respective component.
  

*source Class*
- Similary to the resistor Class, but with the information of the voltage source of the circuit. It will also inheriate
  from the component_manager Class.

*component_loader Class*
- The main control of all the classes. Here we extract the information from the JSON file and create the class objects of each component in the
  circuit and the node Class objects for identifying the position of each component.

*component_manager Class*
- Superclass from which the ressitor and node Class inheriate variables, since there is a direct connection and similar values between the components

## Before Calculations
- We need to ensure that the circuit is completed before calculating the data.
- We need to ensure that:
  1. There is at least 1 voltage source
  2. A complete loop with no components hanging out
  3. A reference node (Ground)
- We also can check that, if two resistors have the same nodes, they are in parallel, but if they have different ones, they are in series. For ensuring consistency, we check how many resistors are in a single node. If there are more than 2, then what can we do?
- We can do this by checks.
  1. Check the amount of components at each node
  2. Check the components that have equivalent nodes
- We can take component A, list its nodes and then do the same with component B and see which are common. If both are, then they are in parallel. If only 1, they are in seires. If neither, then those 
  components are not connected to each other. If parallel, the node could still have more than 2 components, but they can be in parallel as well. If series, the node has to be sharing exactly two components.

- We have to follow a certain restriction for determining parallel or series. We will identify the amount of components in a node as `C`:

1. Parallel
    - C == 2
    - a Node can have > 2 Components and have components in parallel BUT these components must have the same two nodes
2. Series
    - C == 1
    - A node can have == 2 components in the same node, BUT it cannot surpass that limit or be below it 
3. No connection
    - C == 0

- To establish a logic to follow:
  1. Make a dictionary for the nodes that are shared between components
  2. Label each component `series` or `parallel` and to what other component
  3. Calculate after giving a label to each component

- Current progress focuses on creating a temporary list for the components of each node, assign each node as a key and list of components as the value, and then check them to see which nodes have the same components to determine series or parallel.
- Also, the classes for the sources and components in general will have a `tag` for storing a dictionary with a list for the components that are in `series` and another for `parallel`.

- For ensuring series behavior, we check that a node has only two components connected to it. If its true, then those two components are in series.
- For parallel, we must compare the components between all the nodes. Then, we check which components have the same nodes. Those components will be in parallel.

- ENSURE THAT THE NODES ARE NOT CHECKED TWICE, ONLY ONCE (FIX)