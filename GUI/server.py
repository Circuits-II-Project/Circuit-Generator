import os, sys
import copy
import re
import matplotlib
matplotlib.use('Agg')
import schemdraw
import schemdraw.elements as elm
from flask import Flask, send_from_directory, request, jsonify 
from node_calculations.validation import check_circuit
 
# single source of truth: circuits as plain data (same shape as the JSON)
circuit_data = {"components": [], "source": None, "ground": None}
# Node naming state. next_node only goes up
counters = {"next_node": 0, "last_node": None}

#Results of the last rebuild. Never edited by hand, only replaced by commit()
current_load = None
current_analysis = None

#component_type - > schemdraw element used to draw it
DRAW_ELEMENT = {
    "resistor": elm.Resistor,
    "capacitor" : elm.Capacitor,
    "inductor" : elm.Inductor,
}
ID_PREFIX = {"resistor": "R", "capacitor": "C", "inductor": "L"}
DEFAULT_VALUES = {"resistor": 100, "capacitor": 1e-6, "inductor": 0.01}
SOURCE_ID = "V1"
NEW_NODE = "new"   # from_node / to_node value

# The path must be added BEFORE importing loader/analyzer, otherwise Python can't find them
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, '..'))
from node_calculations import loader as cl
from node_calculations import analyzer as al

IMAGE_PATH = os.path.join(HERE, "MyCirc_2.png")

schemdraw.use('matplotlib')

app = Flask(__name__)

app.json.sort_keys = False


class NotFound(LookupError):
    """Asked to change something that isn't there -> 404"""

def commit(change):
   
    global circuit_data, counters, current_load, current_analysis
    draft = copy.deepcopy(circuit_data)
    draft_counters = dict(counters)

    change(draft, draft_counters)                  
    load = cl.components_loader(draft)            
    analysis = al.connection_analyzer(load)

    # Everything passed: swap in the new state all at once
    circuit_data, counters = draft, draft_counters
    current_load, current_analysis = load, analysis
    redraw()

def reset_state(draw=True):
    #Back to an empty circuit
    global circuit_data, counters, current_load, current_analysis
    circuit_data = {"components": [], "source": None, "ground": None}
    counters = {"next_node": 0, "last_node": None}
    current_load = cl.components_loader(circuit_data)
    current_analysis = al.connection_analyzer(current_load)
    if draw:
        redraw()

def next_id(draft, comp_type):
    #Uses the highest existing number so ids stay unique even after removing
    prefix = ID_PREFIX[comp_type]
    used = [int(c["component_id"][len(prefix):])
            for c in draft["components"]
            if c["component_id"].startswith(prefix)]
    return f"{prefix}{max(used, default=0) + 1}"


def resolve_node(name, draft_counters):
    if name == NEW_NODE:
        name = f"N{draft_counters['next_node']}"
        draft_counters["next_node"] += 1
        return name
    if not isinstance(name, str):
        raise ValueError(f"Node names must be text, got {name!r}")
    match = re.fullmatch(r"N(\d+)", name)
    if not match or int(match.group(1)) >= draft_counters["next_node"]:
        raise ValueError(f"Node '{name}' does not exist. Pick an existing node or '{NEW_NODE}'")
    return name

def pick_nodes(from_node, to_node, draft_counters):
    # Defaults: start at the last node (series chain) and end at a brand-new node.
    if not from_node:
        from_node = draft_counters["last_node"] or NEW_NODE
    if not to_node:
        to_node = NEW_NODE
    from_node = resolve_node(from_node, draft_counters)
    to_node = resolve_node(to_node, draft_counters)
    return from_node, to_node


def add_component(comp_type, from_node=None, to_node=None, value=None):
    if comp_type == cl.SOURCE_TYPE:
        return set_source(from_node, to_node, value)

    def change(draft, draft_counters):
        cl.check_type(comp_type)   
        a, b = pick_nodes(from_node, to_node, draft_counters)
        clean_value = cl.validate_component(comp_type, a, b, value)
        _, value_field = cl.COMPONENT_TYPES[comp_type]
        draft["components"].append({
            "component_id": next_id(draft, comp_type),
            "component_type": comp_type,
            "from_node": a,
            "to_node": b,
            value_field: clean_value,
        })
        draft_counters["last_node"] = b
    commit(change)

def set_source(from_node, to_node, value):
    def change(draft, draft_counters):
        a, b = pick_nodes(from_node, to_node, draft_counters)
        volts = cl.validate_component(cl.SOURCE_TYPE, a, b, value, SOURCE_ID)
        draft["source"] = {
            "source_id": SOURCE_ID, "source_type": "DC",
            "source_voltage": volts, "source_frequency": None,
            "from_node": a, "to_node": b,
        }
    commit(change)


def remove_component(comp_id):
    def change(draft, draft_counters):
        before = len(draft["components"])
        draft["components"] = [c for c in draft["components"] if c["component_id"] != comp_id]
        removed = len(draft["components"]) < before
        if draft.get("source") and draft["source"]["source_id"] == comp_id:
            draft["source"] = None
            removed = True
        if not removed:
            raise NotFound(f"There is no component '{comp_id}'")
        if draft.get("ground") and draft["ground"] not in cl.components_loader(draft).nodes:
            draft["ground"] = None
    commit(change)

def set_ground(node):
    def change(draft, draft_counters):
        if not node:
            raise ValueError("Missing field: node")
        if node not in cl.components_loader(draft).nodes:
            raise ValueError(f"Node '{node}' is not part of the circuit, so it cant be ground")
        draft["ground"] = node
    commit(change)

def check_json():
    problems = check_circuit(circuit_data)
    return {"ok": not problems, "problems": problems}

def state_json():
    #Analyzer does the simple data conversion
    out = current_analysis.to_dict()
    out["circuit"] = circuit_data    # raw data, so GUI can show values
    out["source"] = circuit_data.get("source")
    out["ground"] = circuit_data.get("ground")
    out["last_node"] = counters["last_node"]
    out["check"] = check_json()      # so the GUI can enable/disable Calculate
    return out


def redraw():
    path = IMAGE_PATH

    if not circuit_data["components"]:
        if os.path.exists(path):
            os.remove(path)
        return

    with schemdraw.Drawing(file=path, show=False) as d:
        for comp in circuit_data["components"]:
            d += DRAW_ELEMENT[comp["component_type"]]().label(comp["component_id"])





@app.errorhandler(ValueError)
def bad_input(err):
    # Any rejected input: readable message, 400, and the circuit is unchanged
    return jsonify(error=str(err)), 400

@app.errorhandler(NotFound)
def not_found(err):
    return jsonify(error=str(err)), 404


def body():
    return request.get_json(silent=True) or {}


#URL the button will call
@app.route('/add_resistor', methods =['POST'])
def r():
    add_component("resistor", value=DEFAULT_VALUES["resistor"])
    return jsonify(state_json())

@app.route('/add_capacitor', methods=['POST'])
def c():
    add_component("capacitor", value=DEFAULT_VALUES["capacitor"])
    return jsonify(state_json())

@app.route('/add_inductor', methods=['POST'])
def i():
    add_component("inductor", value=DEFAULT_VALUES["inductor"])
    return jsonify(state_json())

# Works for every type, including "source" (which replaces the one source, V1)
@app.route('/add/<comp_type>', methods=['POST'])
def add(comp_type):
    data = body()
    add_component(comp_type, data.get("from_node"), data.get("to_node"), data.get("value"))
    return jsonify(state_json())

@app.route('/ground', methods=['POST'])
def ground():
    set_ground(body().get("node"))
    return jsonify(state_json())
@app.route('/remove/<comp_id>', methods=['POST'])
def remove(comp_id):
    remove_component(comp_id)
    return jsonify(state_json())

@app.route('/reset', methods=['POST'])
def reset():
    reset_state()
    return jsonify(state_json())

@app.route('/state', methods=['GET'])
def state():
    return jsonify(state_json())

@app.route('/check', methods=['GET'])
def check():
    return jsonify(check_json())

#Serve the page and the image
@app.route('/')
def page():
    return send_from_directory(HERE, 'display.html')

@app.route('/MyCirc_2.png')
def image():
    return send_from_directory(HERE, 'MyCirc_2.png')


# Start empty. No redraw here, so importing the server (tests) never touches the image
reset_state(draw=False)

if __name__ == '__main__':
    app.run(debug=True)