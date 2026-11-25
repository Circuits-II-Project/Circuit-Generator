import os, sys
import copy
import re
import matplotlib
matplotlib.use('Agg')
import schemdraw
import schemdraw.elements as elm
from flask import Flask, send_from_directory, request, jsonify

# single source of truth: circuits as plain data (same shape as the JSON)
circuit_data = {"components": [], "source": None, "ground": None}
# Node naming state. next_node only goes up
counters = {"next_node": 0, "last_node": None}

#Results of the last rebuild. Never edited by hand, only replaced by commit()
current_load = None
current_analysis = None

ID_PREFIX = {"resistor": "R", "capacitor": "C", "inductor": "L"}
DEFAULT_VALUES = {"resistor": 100, "capacitor": 1e-6, "inductor": 0.01}
SOURCE_ID = "V1"
NEW_NODE = "new"   # from_node / to_node value

# The path must be added BEFORE importing loader/analyzer, otherwise Python can't find them
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, '..'))
from node_calculations import loader as cl
from node_calculations import analyzer as al
from node_calculations.validation import check_circuit
sys.path.insert(0, HERE)
import drawing   # needs node_calculations on the path, so it comes after the line above

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

def insert_series(comp_id, comp_type, value):
    def change(draft, draft_counters):
        target = next((c for c in draft["components"] if c["component_id"] == comp_id), None)
        if target is None and draft.get("source") and draft["source"]["source_id"] == comp_id:
            target = draft["source"]
        if target is None:
            raise NotFound(f"There is no component '{comp_id}'")
        cl.check_type(comp_type)
        if comp_type == cl.SOURCE_TYPE:
            raise ValueError("Only one source is allowed, so a source can't be added in series")
        old_to = target["to_node"]
        new_node = resolve_node(NEW_NODE, draft_counters)
        target["to_node"] = new_node
        clean_value = cl.validate_component(comp_type, new_node, old_to, value)
        draft["components"].append({
            "component_id": next_id(draft, comp_type),
            "component_type": comp_type,
            "from_node": new_node,
            "to_node": old_to,
            cl.COMPONENT_TYPES[comp_type][1]: clean_value,
        })
    commit(change)

def check_json():
    problems = check_circuit(circuit_data)
    return {"ok": not problems, "problems": problems}

def calculate_json():
    # Simple DC solver: only handles one series loop of resistors and the source.
    problems = check_circuit(circuit_data)
    if problems:
        raise ValueError("The circuit is not ready: " + " ".join(problems))
    parts = circuit_data["components"]
    if any(c["component_type"] != "resistor" for c in parts):
        raise ValueError("Calculate only supports resistors for now")
    if any(len(n.connected_components) != 2 for n in current_load.nodes.values()):
        raise ValueError("Calculate only supports a single series loop for now (no parallel branches)")

    volts = circuit_data["source"]["source_voltage"]
    total_r = sum(c["resistance"] for c in parts)
    current = volts / total_r

    results = {c["component_id"]: {"current": current, "voltage": current * c["resistance"]}
               for c in parts}
    results[SOURCE_ID] = {"current": -current, "voltage": volts}
    return {"components": results, "total_power_delivered": volts * current}

def relation_labels(analysis):
    info = analysis.to_dict()
    labels, seen = [], set()
    for cid, comp in info["components"].items():
        if comp["parallel"]:
            group = tuple(sorted([cid, *comp["parallel"]], key=cl.id_sort_key))
            if group not in seen:
                seen.add(group)
                labels.append("Parallel: " + " ∥ ".join(group))
    for group in info["series_groups"]:
        labels.append("Series: " + " + ".join(group))
    return labels

def state_json():
    out = current_analysis.to_dict()
    out["circuit"] = circuit_data   
    out["source"] = circuit_data.get("source")
    out["ground"] = circuit_data.get("ground")
    out["last_node"] = counters["last_node"]
    out["check"] = check_json()      
    out["labels"] = relation_labels(current_analysis)   
    out["structure"] = drawing.structure(circuit_data) 
    return out


def redraw():
    path = IMAGE_PATH

    #schemdraw crashes saving an empty drawing, so just remove the stale image
    if not circuit_data["components"] and not circuit_data.get("source"):
        if os.path.exists(path):
            os.remove(path)
        return
    try:
        drawing.draw_circuit(circuit_data, path)
    except Exception:
        # A drawing problem must never block editing; the circuit itself is already saved
        app.logger.exception("Could not draw the circuit")



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

@app.route('/insert_series/<comp_id>', methods=['POST'])
def insert_series_route(comp_id):
    data = body()
    insert_series(comp_id, data.get("type"), data.get("value"))
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

@app.route('/calculate', methods=['POST'])
def calculate():
    return jsonify(calculate_json())

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