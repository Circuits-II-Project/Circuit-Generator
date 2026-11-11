import os, sys
import matplotlib
matplotlib.use('Agg')
import schemdraw
import schemdraw.elements as elm
from flask import Flask, send_from_directory

# The path must be added BEFORE importing loader/analyzer, otherwise Python can't find them
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, '..','Node Calculations'))
import loader as cl
import analyzer as al


schemdraw.use('matplotlib')

app = Flask(__name__)

#Every element added so far, so the circuit can grow with each click
parts = []

def redraw():
    with schemdraw.Drawing(file=os.path.join(HERE, 'MyCirc_2.png'), show=False) as d:
        for part in parts:
            d += part()

def add_resistor():
    parts.append(elm.Resistor)
    redraw()

def add_capacitor():
    parts.append(elm.Capacitor)
    redraw()

def add_inductor():
    parts.append(elm.Inductor)
    redraw()


#URL the button will call
@app.route('/add_resistor', methods =['POST'])
def r():
    add_resistor()
    return 'ok'

@app.route('/add_capacitor', methods=['POST'])
def c():
    add_capacitor()
    return 'ok'

@app.route('/add_inductor', methods=['POST'])
def i():
    add_inductor()
    return 'ok'

#Serve the page and the image
@app.route('/')
def page():
    return send_from_directory(HERE, 'display.html')

@app.route('/MyCirc_2.png')
def image():
    return send_from_directory(HERE, 'MyCirc_2.png')

if __name__ == '__main__':
    app.run(debug=True)