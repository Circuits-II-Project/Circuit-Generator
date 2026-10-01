import os
import cmath #for complex number operations
import math
# Wipes the terminal screen completely clean before printing anything else
os.system('cls' if os.name == 'nt' else 'clear')

#AC circuit elements have 3 representations: sinusoidal, rectangular and polar
#the following script will only focus on rectangular and polar for now

def rec_to_pol(real,imaginary): #rectangular to polar representation
    z = complex(real, imaginary)

    magnitude = abs(z) #Returns the absolute value of z

    angle_degrees = math.degrees(cmath.phase(z)) #cmath.phase() returns phase-angle

    return magnitude, angle_degrees

def pol_to_rec(magnitude,angle_degrees): #polar to rectangular representation
    angle_radians = math.radians(angle_degrees)
    z = cmath.rect(magnitude,angle_radians)
    return z.real, z.imag   

def calc_impedance(XC,XL,resistor):
    angle_degrees = math.degrees(math.atan((XL - XC)/(resistor)))
    Z = math.sqrt(pow(XL - XC,2) + pow(resistor,2))

    return Z, angle_degrees

def calc_capacitive_reactance(capacitance,source_frequency):
    XC = 1/(2 * math.pi * source_frequency * capacitance)
    return XC

def calc_inductive_reactance(inductance,source_frequency):
    XL = 2 * math.pi * source_frequency * inductance
    return XL


#------------TEST--------------
C1 = 0.000001
L1 = 4
R1 = 30
frequency = 50

#Lets find the inductive reactance
XL = calc_inductive_reactance(L1,frequency)
print(XL)
#Lets find the capacitive reactance
XC = calc_capacitive_reactance(C1,frequency)
print(XC)

#Let's calculate the impedance
Z = calc_impedance(XC,XL,R1)
print(Z)

magnitude, angle = Z

real, imaginary = pol_to_rec(magnitude, angle)

print("Polar:", magnitude, angle)
print("Rectangular:", real, imaginary)





