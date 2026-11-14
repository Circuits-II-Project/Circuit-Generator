# Testing Calculations
- For ensuring that the equivalent resistance calculations are working correctly, we will change the values in the json file multiple times to ensure that the code is consistent with any type of circuit (or most of them).

## First Set
1. Parallel Circuit [O]
{
    "circuit_id": "C001",
    "circuit_name": "Circuit 1",
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
      "resistance": 100.0,
      "tag": "A"
    },
    {
      "component_id": "R2",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 200.0
    },
    {
      "component_id": "R3",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 300.0
    },
    {
      "component_id": "R4",
      "component_type": "resistor",
      "from_node": "B",
      "to_node": "C",
      "resistance": 300.0
    }
  ]
}

==================================================
               CIRCUIT NODES              
==================================================
  -> Node(ID: A, Voltage: 0V, Connected: ['V1', 'series_parallel_R2_R3_R1_R4'])
  -> Node(ID: B, Voltage: 0V, Connected: ['series_parallel_R2_R3_R1_R4'])
  -> Node(ID: C, Voltage: 0V, Connected: ['V1'])

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
  Component ID : series_parallel_R2_R3_R1_R4
  Type         : resistor
  Connections  : Node A -> Node B
  Resistance   : 354.54545454545456 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------

- Expected output was Recevied. If its calculated by hand, the output will prove to be correct.

2. Pure Series [O]

{
    "circuit_id": "C002",
    "circuit_name": "Pure Series Circuit",
    "circuit_type": "series",
    
    "source": 
    {
        "source_id": "V1",
        "source_type": "DC",
        "source_voltage": 12.0,
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
      "resistance": 100.0
    },
    {
      "component_id": "R2",
      "component_type": "resistor",
      "from_node": "B",
      "to_node": "C",
      "resistance": 200.0
    },
    {
      "component_id": "R3",
      "component_type": "resistor",
      "from_node": "C",
      "to_node": "D",
      "resistance": 300.0
    }
  ]
}
==================================================
               CIRCUIT NODES              
==================================================
  -> Node(ID: A, Voltage: 0V, Connected: ['V1', 'series_R2_R1_R3'])
  -> Node(ID: B, Voltage: 0V, Connected: [])
  -> Node(ID: C, Voltage: 0V, Connected: [])
  -> Node(ID: D, Voltage: 0V, Connected: ['V1', 'series_R2_R1_R3'])

==================================================
         SAVED COMPONENTS & TAGS          
==================================================
  Component ID : V1
  Type         : DC
  Connections  : Node A -> Node D
  Voltage      : 12.0V
  Frequency    : NoneHz
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : series_R2_R1_R3
  Type         : resistor
  Connections  : Node A -> Node D
  Resistance   : 600.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------

- Expected output was received. Calculations by hand will give out the same result.

3. Pure Parallel [O]

{
    "circuit_id": "C003",
    "circuit_name": "Pure Parallel Circuit",
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
      "resistance": 100.0
    },
    {
      "component_id": "R2",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 200.0
    },
    {
      "component_id": "R3",
      "component_type": "resistor",
      "from_node": "A",
      "to_node": "B",
      "resistance": 300.0
    }
  ]
}

==================================================
               CIRCUIT NODES              
==================================================
  -> Node(ID: A, Voltage: 0V, Connected: ['V1', 'parallel_R2_R3_R1'])
  -> Node(ID: B, Voltage: 0V, Connected: ['V1', 'parallel_R2_R3_R1'])

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
  Component ID : parallel_R2_R3_R1
  Type         : resistor
  Connections  : Node A -> Node B
  Resistance   : 54.54545454545455 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
 
 - The test was succesful. The outputted value is correct.

4. Series-Parallel [O]

{
    "circuit_id": "C004",
    "circuit_name": "Series-Parallel Mixed Circuit",
    "circuit_type": "series-parallel",
    
    "source": 
    {
        "source_id": "V1",
        "source_type": "DC",
        "source_voltage": 12.0,
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
      "resistance": 100.0
    },
    {
      "component_id": "R2",
      "component_type": "resistor",
      "from_node": "B",
      "to_node": "C",
      "resistance": 150.0
    },
    {
      "component_id": "R3",
      "component_type": "resistor",
      "from_node": "B",
      "to_node": "C",
      "resistance": 150.0
    },
    {
      "component_id": "R4",
      "component_type": "resistor",
      "from_node": "C",
      "to_node": "D",
      "resistance": 100.0
    }
  ]
}

==================================================
               CIRCUIT NODES              
==================================================
  -> Node(ID: A, Voltage: 0V, Connected: ['V1', 'series_parallel_R3_R2_R1_R4'])
  -> Node(ID: B, Voltage: 0V, Connected: [])
  -> Node(ID: C, Voltage: 0V, Connected: [])
  -> Node(ID: D, Voltage: 0V, Connected: ['V1', 'series_parallel_R3_R2_R1_R4'])

==================================================
         SAVED COMPONENTS & TAGS          
==================================================
  Component ID : V1
  Type         : DC
  Connections  : Node A -> Node D
  Voltage      : 12.0V
  Frequency    : NoneHz
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : series_parallel_R3_R2_R1_R4
  Type         : resistor
  Connections  : Node A -> Node D
  Resistance   : 275.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------

- The test was succesful. The series-parallel calculations worked correctly.

5. Wheatstone Bridge [X]

{
    "circuit_id": "C005",
    "circuit_name": "Wheatstone Bridge Circuit",
    "circuit_type": "bridge",
    
    "source": 
    {
        "source_id": "V1",
        "source_type": "DC",
        "source_voltage": 10.0,
        "source_frequency": null,
        "from_node": "A",
        "to_node": "C"
    },
    
    "nodes": ["A", "B", "C", "D"],
    
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
          "to_node": "D",
          "resistance": 100.0
        },
        {
          "component_id": "R3",
          "component_type": "resistor",
          "from_node": "B",
          "to_node": "C",
          "resistance": 100.0
        },
        {
          "component_id": "R4",
          "component_type": "resistor",
          "from_node": "D",
          "to_node": "C",
          "resistance": 100.0
        },
        {
          "component_id": "R5",
          "component_type": "resistor",
          "from_node": "B",
          "to_node": "D",
          "resistance": 100.0
        }
    ]
}

- This test is to prove the limits of the calculations. A Wheatstone bridge cannot be reduced by convential series-parallel calculations. It would require a different set of steps.

6. Ladder [O]

{
    "circuit_id": "C006",
    "circuit_name": "Multi-Stage Complex Ladder",
    "circuit_type": "ladder",
    
    "source": 
    {
        "source_id": "V1",
        "source_type": "DC",
        "source_voltage": 24.0,
        "source_frequency": null,
        "from_node": "A",
        "to_node": "E"
    },
    
    "nodes": ["A", "B", "C", "D", "E"],
    
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
        },
        {
          "component_id": "R4",
          "component_type": "resistor",
          "from_node": "C",
          "to_node": "D",
          "resistance": 50.0
        },
        {
          "component_id": "R5",
          "component_type": "resistor",
          "from_node": "D",
          "to_node": "E",
          "resistance": 200.0
        },
        {
          "component_id": "R6",
          "component_type": "resistor",
          "from_node": "D",
          "to_node": "E",
          "resistance": 200.0
        }
    ]
}

- The test was succesful, with minor updates tot he reading logic of the parallel and series calculations.


## Second Set



2. Pure Series [O]

Success: Circuit successfully reduced to a single equivalent component!
==================================================
               CIRCUIT NODES              
==================================================
  -> Node(ID: A, Voltage: 0V, Connected: ['V1', 'series_R3_series_R1_R2'])
  -> Node(ID: B, Voltage: 0V, Connected: [])
  -> Node(ID: C, Voltage: 0V, Connected: [])
  -> Node(ID: D, Voltage: 0V, Connected: ['V1', 'series_R3_series_R1_R2'])

==================================================
         SAVED COMPONENTS & TAGS          
==================================================
  Component ID : V1
  Type         : DC
  Connections  : Node A -> Node D
  Voltage      : 12.0V
  Frequency    : NoneHz
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : series_R3_series_R1_R2
  Type         : resistor
  Connections  : Node D -> Node A
  Resistance   : 600.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------


3. Pure Parallel [O]

Success: Circuit successfully reduced to a single equivalent component!
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
  Voltage      : 12.0V
  Frequency    : NoneHz
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : parallel_R1_R2_R3
  Type         : resistor
  Connections  : Node A -> Node B
  Resistance   : 54.54545454545455 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------


4. Series-Parallel [O]

Success: Circuit successfully reduced to a single equivalent component!
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
  Voltage      : 12.0V
  Frequency    : NoneHz
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : series_R4_series_R1_parallel_R2_R3
  Type         : resistor
  Connections  : Node D -> Node A
  Resistance   : 275.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------

5. Wheatstone Bridge [O]

Warning: Circuit could not be fully reduced. 5 unreduced components remaining (possible unhandled topology like a bridge).
==================================================
               CIRCUIT NODES              
==================================================
  -> Node(ID: A, Voltage: 0V, Connected: ['R1', 'R2', 'V1'])
  -> Node(ID: B, Voltage: 0V, Connected: ['R1', 'R3', 'R5'])
  -> Node(ID: D, Voltage: 0V, Connected: ['R2', 'R4', 'R5'])
  -> Node(ID: C, Voltage: 0V, Connected: ['R3', 'R4', 'V1'])

==================================================
         SAVED COMPONENTS & TAGS          
==================================================
  Component ID : R1
  Type         : resistor
  Connections  : Node A -> Node B
  Resistance   : 100.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : R2
  Type         : resistor
  Connections  : Node A -> Node D
  Resistance   : 100.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : R3
  Type         : resistor
  Connections  : Node B -> Node C
  Resistance   : 100.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : R4
  Type         : resistor
  Connections  : Node D -> Node C
  Resistance   : 100.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : R5
  Type         : resistor
  Connections  : Node B -> Node D
  Resistance   : 100.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : V1
  Type         : DC
  Connections  : Node A -> Node C
  Voltage      : 10.0V
  Frequency    : NoneHz
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------

6. Ladder [O]

Success: Circuit successfully reduced to a single equivalent component!
==================================================
               CIRCUIT NODES              
==================================================
  -> Node(ID: A, Voltage: 0V, Connected: ['V1', 'series_R4_parallel_R5_R6_series_R1_parallel_R2_R3'])
  -> Node(ID: B, Voltage: 0V, Connected: [])
  -> Node(ID: C, Voltage: 0V, Connected: [])
  -> Node(ID: D, Voltage: 0V, Connected: [])
  -> Node(ID: E, Voltage: 0V, Connected: ['V1', 'series_R4_parallel_R5_R6_series_R1_parallel_R2_R3'])

==================================================
         SAVED COMPONENTS & TAGS          
==================================================
  Component ID : V1
  Type         : DC
  Connections  : Node A -> Node E
  Voltage      : 24.0V
  Frequency    : NoneHz
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
  Component ID : series_R4_parallel_R5_R6_series_R1_parallel_R2_R3
  Type         : resistor
  Connections  : Node E -> Node A
  Resistance   : 250.0 Ω
  Series Tags  : None
  Parallel Tags: None
--------------------------------------------------
