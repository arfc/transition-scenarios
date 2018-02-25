import numpy as np
import random
import sys

def generate_input(input_path, output_path, orig_lifetime, country):
    """ This function takes a full CYCLUS input xml file,
        finds the DeployInst block for country,
        and extends the lifetime of LWR reactors 
        according to a Gaussian distribution (mean 10, sd 3 [years])

        Parameters
        ----------
        input_path: str
            path for file to be copied and modified
        output_path: str
            path for the modified file
        orig_lifetime: int
            original lifetime for lwrs (to search for)
        country: str
            country (region) to make this change in
        """
    trig = False
    trig2 = False
    # these values are hard-coded for ease of use
    new_file = open(output_path, 'w')
    default_file = open(input_path, 'r')

    for line in default_file:
        if country in line and 'government' in line:
            trig = True
        if trig and 'lifetime' in line:
            trig2 = True
        if trig2:
            if '</lifetimes>' in line:
                trig2 = False
                trig = False
            else:
                if ('<val>%i</val>' %orig_lifetime in line):
                    # this is where we add the random
                    lifetime_extension = abs(int(np.random.normal(10, 6)))
                    lifetime = 720 + lifetime_extension * 12
                    new_file.write('<val>%i</val>\n' % lifetime)
                    continue
        new_file.write(line)

    new_file.close()
    default_file.close()

generate_input('../2017-bae-europe/eu_future/default_input_file.xml',
              sys.argv[1], 720, 'France')