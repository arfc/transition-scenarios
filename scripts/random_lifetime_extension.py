import numpy as np
import random

""" This script takes a full CYCUS input xml file,
    finds the DeployInst block for `France_government`,
    and extends the lifetime of LWR reactors (with original lifetime 720)
    according to a Gaussian distribution (mean 10, sd 3 [years])"""
trig = False
trig2= False
# these values are hard-coded for ease of use
new_file = open('../2017-bae-europe/randomly_extended_french_lwrs.xml', 'w')
default_file = open('../2017-bae-europe/default_input_file.xml', 'r')

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

new_file.close()
default_file.close()