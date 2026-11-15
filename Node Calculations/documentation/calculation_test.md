# Testing the Voltage and Current calculations

1. Pure Series Circuit []

{
    "circuit_id": "C002",
    "circuit_name": "Circuit 2",
    "circuit_type": "series",
    
    "source": 
    {
        "source_id": "V1",
        "source_type": "DC",
        "source_voltage": 12.0,
        "source_frequency": null,
        "from_node": "A",
        "to_node": "C"
    },
    
    "nodes": ["A", "B", "C"],
    
    "components": [
    {
      "component_id": "R1",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 100.0
    },
    {
      "component_id": "R2",
      "component_type": "resistor",
      "from_node": "B",
      "to_node": "C",
      "resistance": 200.0
    }
  ]
}

Success: Circuit successfully reduced to a single equivalent component!

============================================================
           CIRCUIT SOLVER: VOLTAGES & CURRENTS          
============================================================
Component ID    | Voltage (V)     | Current (A)
------------------------------------------------------------
R1              | 4.00            | 0.0400 A
R2              | 8.00            | 0.0400 A
series_R1_R2    | 12.00           | 0.0400 A
============================================================
==================================================
               CIRCUIT NODES              
==================================================
  -> Node(ID: A, Voltage: 0V, Connected: ['V1', 'series_R1_R2'])
  -> Node(ID: B, Voltage: 0V, Connected: [])
  -> Node(ID: C, Voltage: 0V, Connected: ['V1', 'series_R1_R2'])

==================================================
         SAVED COMPONENTS & TAGS          
==================================================
  Component ID : V1
  Type         : DC
  Connections  : Node A -> Node C
  Voltage      : 12.0V
  Frequency    : NoneHz
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : series_R1_R2
  Type         : resistor
  Connections  : Node A -> Node C
  Resistance   : 300.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------

2. Pure Parallel Circuit []

{
    "circuit_id": "C003",
    "circuit_name": "Circuit 3",
    "circuit_type": "parallel",
    
    "source": 
    {
        "source_id": "V1",
        "source_type": "DC",
        "source_voltage": 10.0,
        "source_frequency": null,
        "from_node": "A",
        "to_node": "B"
    },
    
    "nodes": ["A", "B"],
    
    "components": [
    {
      "component_id": "R1",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 100.0
    },
    {
      "component_id": "R2",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 100.0
    },
    {
      "component_id": "R3",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 100.0
    }
  ]
}

Success: Circuit successfully reduced to a single equivalent component!

============================================================
           CIRCUIT SOLVER: VOLTAGES & CURRENTS          
============================================================
Component ID    | Voltage (V)     | Current (A)
------------------------------------------------------------
R1              | 10.00           | 0.1000 A
R2              | 10.00           | 0.1000 A
R3              | 10.00           | 0.1000 A
parallel_R1_R2_R3 | 10.00           | 0.3000 A
============================================================
==================================================
               CIRCUIT NODES              
==================================================
  -> Node(ID: A, Voltage: 0V, Connected: ['V1', 'parallel_R1_R2_R3'])
  -> Node(ID: B, Voltage: 0V, Connected: ['V1', 'parallel_R1_R2_R3'])

==================================================
         SAVED COMPONENTS & TAGS          
==================================================
  Component ID : V1
  Type         : DC
  Connections  : Node A -> Node B
  Voltage      : 10.0V
  Frequency    : NoneHz
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : parallel_R1_R2_R3
  Type         : resistor
  Connections  : Node A -> Node B
  Resistance   : 33.333333333333336 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------

3. Parallel Group Followed by Series Resistor []

{
    "circuit_id": "C004",
    "circuit_name": "Circuit 4",
    "circuit_type": "series",
    
    "source": 
    {
        "source_id": "V1",
        "source_type": "DC",
        "source_voltage": 24.0,
        "source_frequency": null,
        "from_node": "A",
        "to_node": "C"
    },
    
    "nodes": ["A", "B", "C"],
    
    "components": [
    {
      "component_id": "R1",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 60.0
    },
    {
      "component_id": "R2",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 60.0
    },
    {
      "component_id": "R3",
      "component_type": "resistor",
      "from_node": "B",
      "to_node": "C",
      "resistance": 30.0
    }
  ]
}

Success: Circuit successfully reduced to a single equivalent component!

============================================================
           CIRCUIT SOLVER: VOLTAGES & CURRENTS          
============================================================
Component ID    | Voltage (V)     | Current (A)
------------------------------------------------------------
R1              | 12.00           | 0.2000 A
R2              | 12.00           | 0.2000 A
R3              | 12.00           | 0.4000 A
parallel_R1_R2  | 12.00           | 0.4000 A
series_R3_parallel_R1_R2 | 24.00           | 0.4000 A
============================================================
==================================================
               CIRCUIT NODES              
==================================================
  -> Node(ID: A, Voltage: 0V, Connected: ['V1', 'series_R3_parallel_R1_R2'])
  -> Node(ID: B, Voltage: 0V, Connected: [])
  -> Node(ID: C, Voltage: 0V, Connected: ['V1', 'series_R3_parallel_R1_R2'])

==================================================
         SAVED COMPONENTS & TAGS          
==================================================
  Component ID : V1
  Type         : DC
  Connections  : Node A -> Node C
  Voltage      : 24.0V
  Frequency    : NoneHz
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : series_R3_parallel_R1_R2
  Type         : resistor
  Connections  : Node C -> Node A
  Resistance   : 60.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------

4. Asymmetric Parallel Branches []

{
    "circuit_id": "C005",
    "circuit_name": "Circuit 5",
    "circuit_type": "parallel",
    
    "source": 
    {
        "source_id": "V1",
        "source_type": "DC",
        "source_voltage": 12.0,
        "source_frequency": null,
        "from_node": "A",
        "to_node": "B"
    },
    
    "nodes": ["A", "B"],
    
    "components": [
    {
      "component_id": "R1",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 40.0
    },
    {
      "component_id": "R2",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 60.0
    }
  ]
}

Success: Circuit successfully reduced to a single equivalent component!

============================================================
           CIRCUIT SOLVER: VOLTAGES & CURRENTS          
============================================================
Component ID    | Voltage (V)     | Current (A)
------------------------------------------------------------
R1              | 12.00           | 0.3000 A
R2              | 12.00           | 0.2000 A
parallel_R1_R2  | 12.00           | 0.5000 A
============================================================
==================================================
               CIRCUIT NODES              
==================================================
  -> Node(ID: A, Voltage: 0V, Connected: ['V1', 'parallel_R1_R2'])
  -> Node(ID: B, Voltage: 0V, Connected: ['V1', 'parallel_R1_R2'])

==================================================
         SAVED COMPONENTS & TAGS          
==================================================
  Component ID : V1
  Type         : DC
  Connections  : Node A -> Node B
  Voltage      : 12.0V
  Frequency    : NoneHz
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : parallel_R1_R2
  Type         : resistor
  Connections  : Node A -> Node B
  Resistance   : 23.999999999999996 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------

5. Series Resistor Leading Into a Parallel Split

{
    "circuit_id": "C006",
    "circuit_name": "Circuit 6",
    "circuit_type": "series",
    
    "source": 
    {
        "source_id": "V1",
        "source_type": "DC",
        "source_voltage": 15.0,
        "source_frequency": null,
        "from_node": "A",
        "to_node": "C"
    },
    
    "nodes": ["A", "B", "C"],
    
    "components": [
    {
      "component_id": "R1",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 50.0
    },
    {
      "component_id": "R2",
      "component_type": "resistor",
      "from_node": "B",
      "to_node": "C",
      "resistance": 100.0
    },
    {
      "component_id": "R3",
      "component_type": "resistor",
      "from_node": "B",
      "to_node": "C",
      "resistance": 100.0
    }
  ]
}

Success: Circuit successfully reduced to a single equivalent component!

============================================================
           CIRCUIT SOLVER: VOLTAGES & CURRENTS          
============================================================
Component ID    | Voltage (V)     | Current (A)
------------------------------------------------------------
R1              | 7.50            | 0.1500 A
R2              | 7.50            | 0.0750 A
R3              | 7.50            | 0.0750 A
parallel_R2_R3  | 7.50            | 0.1500 A
series_R1_parallel_R2_R3 | 15.00           | 0.1500 A
============================================================
==================================================
               CIRCUIT NODES              
==================================================
  -> Node(ID: A, Voltage: 0V, Connected: ['V1', 'series_R1_parallel_R2_R3'])
  -> Node(ID: B, Voltage: 0V, Connected: [])
  -> Node(ID: C, Voltage: 0V, Connected: ['V1', 'series_R1_parallel_R2_R3'])

==================================================
         SAVED COMPONENTS & TAGS          
==================================================
  Component ID : V1
  Type         : DC
  Connections  : Node A -> Node C
  Voltage      : 15.0V
  Frequency    : NoneHz
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : series_R1_parallel_R2_R3
  Type         : resistor
  Connections  : Node A -> Node C
  Resistance   : 100.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------


6. Multi-Tier Series-Parallel Circuit []

{
    "circuit_id": "C007",
    "circuit_name": "Circuit 7",
    "circuit_type": "series",
    
    "source": 
    {
        "source_id": "V1",
        "source_type": "DC",
        "source_voltage": 20.0,
        "source_frequency": null,
        "from_node": "A",
        "to_node": "D"
    },
    
    "nodes": ["A", "B", "C", "D"],
    
    "components": [
    {
      "component_id": "R1",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 20.0
    },
    {
      "component_id": "R2",
      "component_type": "resistor",
      "from_node": "B",
      "to_node": "C",
      "resistance": 60.0
    },
    {
      "component_id": "R3",
      "component_type": "resistor",
      "from_node": "B",
      "to_node": "C",
      "resistance": 60.0
    },
    {
      "component_id": "R4",
      "component_type": "resistor",
      "from_node": "C",
      "to_node": "D",
      "resistance": 20.0
    }
  ]
}

Success: Circuit successfully reduced to a single equivalent component!

============================================================
           CIRCUIT SOLVER: VOLTAGES & CURRENTS          
============================================================
Component ID    | Voltage (V)     | Current (A)
------------------------------------------------------------
R1              | 5.71            | 0.2857 A
R2              | 8.57            | 0.1429 A
R3              | 8.57            | 0.1429 A
R4              | 5.71            | 0.2857 A
parallel_R2_R3  | 8.57            | 0.2857 A
series_R1_parallel_R2_R3 | 14.29           | 0.2857 A
series_R4_series_R1_parallel_R2_R3 | 20.00           | 0.2857 A
============================================================
==================================================
               CIRCUIT NODES              
==================================================
  -> Node(ID: A, Voltage: 0V, Connected: ['V1', 'series_R4_series_R1_parallel_R2_R3'])
  -> Node(ID: B, Voltage: 0V, Connected: [])
  -> Node(ID: C, Voltage: 0V, Connected: [])
  -> Node(ID: D, Voltage: 0V, Connected: ['V1', 'series_R4_series_R1_parallel_R2_R3'])

==================================================
         SAVED COMPONENTS & TAGS          
==================================================
  Component ID : V1
  Type         : DC
  Connections  : Node A -> Node D
  Voltage      : 20.0V
  Frequency    : NoneHz
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : series_R4_series_R1_parallel_R2_R3
  Type         : resistor
  Connections  : Node D -> Node A
  Resistance   : 70.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
