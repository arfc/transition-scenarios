import numpy as np
import random

trig = False
trig2= False
new_file = open('./random_lifetime_extension.xml', 'w')
default_file = open('./default_input_file.xml', 'r')

for line in default_file:
    if 'France_government' in line:
        trig = True
    if trig and 'lifetime' in line:
        trig2 = True
    if trig2:
        if '</lifetimes>' in line:
            trig2 = False
            trig = False
        else:
            if ('<val>720</val>' in line):
                # this is where we add the random
                lifetime_extension = abs(int(np.random.normal(10, 3)))
                print(lifetime_extension)
                lifetime = 720 + lifetime_extension * 12
                new_file.write('<val>%i</val>\n' %lifetime)
                continue
    new_file.write(line)
