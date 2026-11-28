import os
import threading
import copy
import numpy as np
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

HERE = os.path.dirname(os.path.abspath(__file__))
from core import loader as cl
from core import analyzer as al
from core.validation import check_circuit
from core.circuit_storage import (
    circuit_identity,
    get_circuit,
    list_circuits,
    resolve_diagram_path,
    save_circuit,
    update_circuit,
)
from . import drawing

IMAGE_PATH = os.path.join(HERE, "static", "MyCirc_2.png")
# Saved image references are relative to this collection's directory.
CIRCUIT_STORAGE_PATH = os.path.join(HERE, "saved_circuits.json")
current_diagram_circuit_id = None
# ``None`` means edits belong to an unsaved/new circuit. Loading or saving a
# document selects it so that a later PUT updates that exact record.
current_record_id = None

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
    global circuit_data, counters, current_load, current_analysis, current_diagram_circuit_id, current_record_id
    circuit_data = {"components": [], "source": None, "ground": None}
    counters = {"next_node": 0, "last_node": None}
    current_load = cl.components_loader(circuit_data)
    current_analysis = al.connection_analyzer(current_load)
    current_diagram_circuit_id = None
    current_record_id = None
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
    # DC solver (nodal analysis): any resistor network with one source and a ground.
    problems = check_circuit(circuit_data)
    if problems:
        raise ValueError("The circuit is not ready: " + " ".join(problems))
    parts = circuit_data["components"]
    if any(c["component_type"] != "resistor" for c in parts):
        raise ValueError("Calculate only supports resistors for now")

    src = circuit_data["source"]
    ground = circuit_data["ground"]
    nodes = sorted({n for c in parts for n in (c["from_node"], c["to_node"])}
                   | {src["from_node"], src["to_node"]}, key=cl.id_sort_key)
    unknown = [n for n in nodes if n != ground]
    idx = {n: i for i, n in enumerate(unknown)}
    k = len(unknown)                      # extra unknown: current through the source
    A = np.zeros((k + 1, k + 1))
    z = np.zeros(k + 1)

    for c in parts:                       # resistor stamps, conductance g = 1/R
        g = 1.0 / c["resistance"]
        a, b = c["from_node"], c["to_node"]
        if a in idx: A[idx[a], idx[a]] += g
        if b in idx: A[idx[b], idx[b]] += g
        if a in idx and b in idx:
            A[idx[a], idx[b]] -= g
            A[idx[b], idx[a]] -= g

    p, n = src["from_node"], src["to_node"]   # source: V(p) - V(n) = volts
    if p in idx:
        A[idx[p], k] += 1
        A[k, idx[p]] += 1
    if n in idx:
        A[idx[n], k] -= 1
        A[k, idx[n]] -= 1
    z[k] = src["source_voltage"]

    try:
        sol = np.linalg.solve(A, z)
    except np.linalg.LinAlgError:
        raise ValueError("The circuit can't be solved (check for floating parts)")

    volt = {n_: 0.0 for n_ in nodes}
    for n_, i in idx.items():
        volt[n_] = float(sol[i])

    results = {}
    for c in parts:
        v = volt[c["from_node"]] - volt[c["to_node"]]
        i = v / c["resistance"]
        results[c["component_id"]] = {"voltage": v, "current": i, "power": v * i}
    v_src = volt[p] - volt[n]
    i_src = float(sol[k])                 # From -> To through the source (negative = delivering)
    results[SOURCE_ID] = {"voltage": v_src, "current": i_src, "power": v_src * i_src}

    absorbed = sum(r["power"] for cid, r in results.items() if cid != SOURCE_ID)
    return {"ground": ground, "node_voltages": volt, "components": results,
            "total_power_delivered": -results[SOURCE_ID]["power"],
            "total_power_absorbed": absorbed}

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
    out["loaded_record_id"] = current_record_id
    return out


def redraw():
    global current_diagram_circuit_id
    path = IMAGE_PATH

    #schemdraw crashes saving an empty drawing, so just remove the stale image
    if not circuit_data["components"] and not circuit_data.get("source"):
        if os.path.exists(path):
            os.remove(path)
        current_diagram_circuit_id = None
        return
    try:
        drawing.draw_circuit(circuit_data, path)
        # This is set only after drawing succeeds, so saving cannot associate a
        # stale working image with newer circuit data.
        current_diagram_circuit_id = circuit_identity(circuit_data)
    except Exception:
        current_diagram_circuit_id = None
        if os.path.exists(path):
            os.remove(path)
        # A drawing problem must never block editing; the circuit itself is already saved
        app.logger.exception("Could not draw the circuit")


def _ready_circuit_snapshot() -> tuple[dict, dict]:
    """Return the editable circuit and fresh results only when both are valid."""
    problems = check_circuit(circuit_data)
    if problems:
        raise ValueError("The circuit is not ready: " + " ".join(problems))

    snapshot = copy.deepcopy(circuit_data)
    if current_diagram_circuit_id != circuit_identity(snapshot):
        raise ValueError(
            "No current diagram is available. Add or change a circuit part to generate it first."
        )
    # calculate_json uses the same committed circuit_data as the snapshot above;
    # validation prevents saving a partial circuit without real results.
    return snapshot, calculate_json()


def save_current_circuit(circuit_name: str) -> dict:
    """Save the current circuit as a new named document."""
    global current_record_id
    snapshot, results = _ready_circuit_snapshot()
    record = save_circuit(
        CIRCUIT_STORAGE_PATH, circuit_name, snapshot, results, IMAGE_PATH, counters
    )
    current_record_id = record["record_id"]
    return record


def update_current_circuit(record_id: str, circuit_name: str | None = None) -> dict:
    """Update the loaded document without creating another record."""
    global current_record_id
    if record_id != current_record_id:
        raise ValueError("Load the circuit before updating it.")
    snapshot, results = _ready_circuit_snapshot()
    record = update_circuit(
        CIRCUIT_STORAGE_PATH, record_id, snapshot, results, IMAGE_PATH,
        counters, circuit_name,
    )
    current_record_id = record["record_id"]
    return record


def load_saved_circuit(record_id: str) -> tuple[dict, bool]:
    """Restore a validated record transactionally and redraw from its data."""
    global circuit_data, counters, current_load, current_analysis, current_record_id
    record = get_circuit(CIRCUIT_STORAGE_PATH, record_id)
    if record is None:
        raise NotFound("Saved circuit was not found.")

    # Validate/rebuild before changing any live server state. The stored PNG is
    # never input to the model; it remains an archival artifact.
    snapshot = copy.deepcopy(record["circuit"])
    restored_counters = dict(record["editor_state"])
    load = cl.components_loader(snapshot)
    analysis = al.connection_analyzer(load)
    circuit_data, counters = snapshot, restored_counters
    current_load, current_analysis, current_record_id = load, analysis, record["record_id"]
    redraw()
    image_available = resolve_diagram_path(CIRCUIT_STORAGE_PATH, record).is_file()
    return record, image_available



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
    problems = check_circuit(circuit_data)
    if problems:
        return jsonify({
            "error": "The circuit is not ready: " + " ".join(problems),
            "problems": problems
        }), 400
    return jsonify(calculate_json())


def circuit_response(record: dict, *, image_available: bool | None = None) -> dict:
    """Build the document response shared by save, update, and load routes."""
    if image_available is None:
        image_available = resolve_diagram_path(CIRCUIT_STORAGE_PATH, record).is_file()
    return {
        "record": record,
        "image_available": image_available,
        "state": state_json(),
    }


@app.route('/circuits', methods=['GET'])
def circuits():
    """List selector metadata; circuit payloads stay behind the detail route."""
    return jsonify({"circuits": list_circuits(CIRCUIT_STORAGE_PATH)})


@app.route('/circuits', methods=['POST'])
def save_circuit_route():
    """Save the current circuit as a new document, even with a repeated name."""
    record = save_current_circuit(body().get("circuit_name"))
    return jsonify(circuit_response(record)), 201


@app.route('/circuits/<record_id>', methods=['GET'])
def circuit(record_id):
    """Return one saved document without changing the editable circuit."""
    record = get_circuit(CIRCUIT_STORAGE_PATH, record_id)
    if record is None:
        raise NotFound("Saved circuit was not found.")
    return jsonify({
        "record": record,
        "image_available": resolve_diagram_path(CIRCUIT_STORAGE_PATH, record).is_file(),
    })


@app.route('/circuits/<record_id>', methods=['PUT'])
def update_circuit_route(record_id):
    """Update the loaded document; POST /circuits is always save-as-new."""
    data = body()
    record = update_current_circuit(record_id, data.get("circuit_name"))
    return jsonify(circuit_response(record))


@app.route('/circuits/<record_id>/load', methods=['POST'])
def load_circuit_route(record_id):
    """Restore saved model data into the editable server state."""
    record, image_available = load_saved_circuit(record_id)
    response = circuit_response(record, image_available=image_available)
    if not image_available:
        response["warning"] = "Saved image is missing; the circuit was redrawn from its data."
    return jsonify(response)


@app.route('/save', methods=['POST'])
def save():
    """Compatibility alias; clients must now send a non-empty circuit_name."""
    record = save_current_circuit(body().get("circuit_name"))
    return jsonify(circuit_response(record)), 201

#Serve the page and the image
@app.route('/')
def landing():
    return send_from_directory(HERE, 'landing.html')

@app.route('/builder')
def page():
    return send_from_directory(HERE, 'display.html')

@app.route('/MyCirc_2.png')
def image():
    return send_from_directory(os.path.join(HERE, "static"), 'MyCirc_2.png')

@app.route('/quit', methods=['POST'])
def quit_app():
    threading.Timer(0.3, lambda: os._exit(0)).start()
    return jsonify({"ok": True})

# Start empty. No redraw here, so importing the server (tests) never touches the image
reset_state(draw=False)

if __name__ == '__main__':
    app.run(debug=True)
