import os, sys
import matplotlib
matplotlib.use('Agg')
import schemdraw
import schemdraw.elements as elm
from flask import Flask, send_from_directory, request, jsonify 
 
# single source of truth: circuits as plain data (same shape as the JSON)
circuit_data = {"components": [], "source":None}

#Results of the last rebuild. Never edited by hand, only replaced by rebuild()
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

# Default node naming. The counter only goes up, so removing a component never
# causes a new one to reuse old node names (which would silently put it in parallel).
last_node = "N0"
node_count = 0


# The path must be added BEFORE importing loader/analyzer, otherwise Python can't find them
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, '..','Node Calculations'))
import loader as cl
import analyzer as al


schemdraw.use('matplotlib')

app = Flask(__name__)


def rebuild():
    #Remove all previous objs and recompute everything from circuit_data
    global current_load, current_analysis
    current_load = cl.components_loader(circuit_data)
    current_analysis = al.connection_analyzer(current_load)
    redraw()

def next_id(comp_type):
    #Uses the highest existing number do ids stay unique even after removing
    prefix = ID_PREFIX[comp_type]
    used = [int (c["component_id"][len(prefix):])
            for c in circuit_data["components"]
            if c["component_id"].startswith(prefix)]
    return f"{prefix}{max(used,default=0) +1}"

def add_component(comp_type, from_node = None, to_node = None, value = None):
    global last_node, node_count
    _, value_field = cl.COMPONENT_TYPES[comp_type]

    # By default, chain onto the last node (series), ending at a brand-new node
    if not from_node:
        from_node = last_node
    if not to_node:
        node_count += 1
        to_node = f"N{node_count}"
    last_node = to_node

    circuit_data["components"].append({
        "component_id": next_id(comp_type),
        "component_type": comp_type,
        "from_node": from_node,
        "to_node": to_node,
        value_field: value if value is not None else DEFAULT_VALUES[comp_type],
    })
    rebuild()

def tags_as_json():
    #objs cant go through jsonify so send only the ids
    return{
        cid: {kind: [other.id for other in others] for kind, others in comp.tag.items()}
        for cid, comp in current_load.components.items()
        }


def redraw():
    path = os.path.join(HERE, "MyCirc_2.png")

    # schemdraw crashes saving an empty drawing, so just remove the stale image
    if not circuit_data["components"]:
        if os.path.exists(path):
            os.remove(path)
        return

    with schemdraw.Drawing(file=path, show=False) as d:
        for comp in circuit_data["components"]:
            d += DRAW_ELEMENT[comp["component_type"]]().label(comp["component_id"])


#URL the button will call
@app.route('/add_resistor', methods =['POST'])
def r():
    add_component("resistor")
    return jsonify(tags_as_json())

@app.route('/add_capacitor', methods=['POST'])
def c():
    add_component("capacitor")
    return jsonify(tags_as_json())

@app.route('/add_inductor', methods=['POST'])
def i():
    add_component("inductor")
    return jsonify(tags_as_json())

@app.route('/add/<comp_type>', methods=['POST'])
def add(comp_type):
    if comp_type not in cl.COMPONENT_TYPES:
        return jsonify(errors=f"unknown type '{comp_type}'"), 400
    body = request.get_json(silent=True) or {}
    if body.get("from_node") and body.get("from_node") == body.get("to_node"):
        return jsonify(errors="from_node and to_node must be different"), 400
    add_component(comp_type, body.get("from_node"), body.get("to_node"), body.get("value"))
    return jsonify(tags_as_json())

@app.route('/remove/<comp_id>', methods=['POST'])
def remove(comp_id):
    circuit_data["components"] = [c for c in circuit_data["components"]
                                  if c ["component_id"] != comp_id]
    rebuild()
    return jsonify(tags_as_json())

#Serve the page and the image
@app.route('/')
def page():
    return send_from_directory(HERE, 'display.html')

@app.route('/MyCirc_2.png')
def image():
    return send_from_directory(HERE, 'MyCirc_2.png')

if __name__ == '__main__':
    app.run(debug=True)