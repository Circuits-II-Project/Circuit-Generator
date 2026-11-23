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

    change(draft, draft_counters)                  # may raise ValueError (bad input)
    load = cl.components_loader(draft)             # may raise ValueError (bad data)
    analysis = al.connection_analyzer(load)

    # Everything passed: swap in the new state all at once
    circuit_data, counters = draft, draft_counters
    current_load, current_analysis = load, analysis
    redraw()