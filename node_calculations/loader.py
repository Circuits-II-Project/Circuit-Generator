import json 
import math
import re
from numbers import Real
from . import components as cmps

# component_type -> class to create, JSON field that holds its value
# To support a new component add one line here.

COMPONENT_TYPES = {
    "resistor": (cmps.resistor, "resistance"),
    "capacitor": (cmps.capacitor, "capacitance"),
    "inductor": (cmps.inductor, "inductance"),
}

SOURCE_TYPE = "source"

def check_type(comp_type, comp_id=None):
    prefix = f"{comp_id}: " if comp_id else ""
    if comp_type is None or (isinstance(comp_type, str) and not comp_type.strip()):
        raise ValueError(f"{prefix}Missing field: component type")
    if comp_type not in COMPONENT_TYPES and comp_type != SOURCE_TYPE:
        allowed = ", ".join([*COMPONENT_TYPES, SOURCE_TYPE])
        raise ValueError(f"{prefix}Unknown component type '{comp_type}'. Use one of: {allowed}")

def validate_component(comp_type, from_node, to_node, value, comp_id=None):
    """Check one component before it is added. Raises ValueError with a readable
    message, or returns the value as a float when everything is fine."""
    prefix = f"{comp_id}: " if comp_id else ""

    def missing(field):
        return field is None or (isinstance(field, str) and not field.strip())

    # Order: type, then nodes, then value.
    check_type(comp_type, comp_id)

    for name, field in (("from_node", from_node), ("to_node", to_node)):
        if missing(field):
            raise ValueError(f"{prefix}Missing field: {name}")

    if from_node == to_node:
        raise ValueError(f"{prefix}A component cannot connect a node to itself ({from_node})")

    if missing(value):
        raise ValueError(f"{prefix}Missing field: value")

    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{prefix}Value must be a number, got {value!r}")
    if not math.isfinite(value):
        raise ValueError(f"{prefix}Value must be a finite number, got {value!r}")
    if value <= 0:
        raise ValueError(f"{prefix}Value must be greater than 0, got {value}")

    return float(value)

def id_sort_key(item_id):
    """Sort key that orders IDs by their number"""
    match = re.fullmatch(r"([^\d]*)(\d*)(.*)", str(item_id))
    letters, number, rest = match.groups()
    return (letters, int(number) if number else -1, rest)

# Reads a circuit JSON file and returns its contents as a dict (outside the class on purpose).
def load_from_file(path: str) -> dict:
    with open(path,'r') as file:
        return json.load(file)

# Central class in which we create each component and node object from the circuit data (a dict).
# The data can come from a file (load_from_file) or directly from the GUI in memory.
class components_loader:
    def __init__(self,data: dict):

        self.data = data
        self.nodes = {}
        self.components = {}
        self.format_component()
        self.format_source()

    # Extract each dictionary from the components list and create the right class for its type
    def format_component(self):
        for comp in self.data.get("components", []):

            comp_type = comp.get("component_type")
            if comp_type == SOURCE_TYPE:
                raise ValueError(f"{comp.get('component_id')}: put the voltage source in the 'source' field, not in 'components'")
            value_field = COMPONENT_TYPES[comp_type][1] if comp_type in COMPONENT_TYPES else None
            # Same rules as the server, so a JSON file can't sneak in bad data either
            validate_component(comp_type, comp.get("from_node"), comp.get("to_node"),
                               comp.get(value_field), comp.get("component_id"))
            cls = COMPONENT_TYPES[comp_type][0]

            comp_obj = cls(
                comp["component_id"],
                comp_type,
                comp["from_node"],
                comp["to_node"],
                comp[value_field],
                {"series": [], "parallel": []}
            )            

            self.components[comp_obj.id] = comp_obj
            self.add_component_node(comp_obj.from_node, comp_obj)
            self.add_component_node(comp_obj.to_node, comp_obj)
        
    def format_source(self):
        #User may not have added any sources yet, so it is optional

        if "source" not in self.data or self.data["source"] is None:
            return
        
        src = self.data["source"]
        validate_component(SOURCE_TYPE, src.get("from_node"), src.get("to_node"),
                           src.get("source_voltage"), src.get("source_id"))
        source_obj = cmps.source(
            src["source_id"],
            src["source_type"],
            src["from_node"],
            src["to_node"],
            src["source_voltage"],
            src.get("source_frequency"), #dc may not have one
            {"series": [], "parallel": []}
        )
        self.components[source_obj.id] = source_obj
        self.add_component_node(source_obj.from_node, source_obj)
        self.add_component_node(source_obj.to_node, source_obj)
        
        
    def add_component_node(self, node_id, component):
        
        if node_id not in self.nodes:
            self.nodes[node_id] = cmps.node(node_id, 0)
        
        self.nodes[node_id].connected_components.append(component)
