import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt

#Seen through matplotlib instead of outside link
schemdraw.use('matplotlib')

def draw1():
    # file= saves on exit; windows are shown together at the end via plt.show()
    with schemdraw.Drawing(file='my_circuit.png', show=False) as d:
        d += elm.Capacitor().label('C1')
        d += elm.Dot()
        with d.hold():
            elm.Resistor().label('R5').down(3).dot()
        d += elm.Resistor().label('R1')
        d += elm.Resistor().label('R2').down()
        d += elm.Resistor().label('R3')
        d += elm.Capacitor().label('C2').left()
        d += elm.Dot()
        with d.hold():
            elm.Resistor().label('R4').up(3)
        d += elm.Resistor().label('R6').left()
        d += elm.Ground()
        d += elm.Battery().label('V').up(6)

def draw2():
    with schemdraw.Drawing(file= 'my_circuit2.png', show=False) as d:
        I1 = elm.SourceI().label('5∠0° A').dot()
        with d.hold():
            elm.Capacitor().right().label('-j3Ω').dot()
            elm.Inductor().down().label('j2Ω').dot().hold()
            elm.Resistor().right().label('5Ω').dot()
            V1 = elm.SourceV().down().reverse().label('5∠-90° V', loc='bot')
            elm.Line().tox(I1.start)
        elm.Line().up(d.unit*.8)
        L1 = elm.Inductor().tox(V1.start).label('j3Ω')
        elm.Line().down(d.unit*.8)
        elm.CurrentLabel(top=False, ofst=.3).at(L1).label('$i_g$')

def add_resistor():
    with schemdraw.Drawing(file = 'MyCirc_2.png', show = False) as d:
            elm.Resistor() 
def add_capacitor():
    with schemdraw.Drawing(file = 'MyCirc_2.png', show = False) as d:
            elm.Capacitor() 
def add_inductor():
    with schemdraw.Drawing(file = 'MyCirc_2.png', show = False) as d:
            elm.Inductor() 

if __name__ == '__main__':
    #draw1()
    #draw2()

    ask1 = input("Type what you would like to add to your circuit:").lower()
    if ask1 == 'r':
        with schemdraw.Drawing(file = 'MyCirc_2.png', show = False) as d:
            elm.Resistor() 
    elif ask1 == 'i':
        with schemdraw.Drawing(file = 'MyCirc_2.png', show = False) as d:
            elm.Inductor()     
    else: 
        print("okay bye!")


    # Keep both figure windows open until closed
    plt.show()
