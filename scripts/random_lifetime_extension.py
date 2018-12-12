import numpy as np
import random
import sys


def generate_input(input_path, output_path, orig_lifetime,
                   country, low=0, high=25):
    """This function takes a full Cyclus input xml file,
        finds the DeployInst block for the country,
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
    new_file = open(output_path, 'w')
    default_file = open(input_path, 'r')

    file_lines = default_file.readlines()
    new_lines = file_lines[:]

    # find line number with the start of  lifetime definition
    for linenum, lines in enumerate(file_lines):
        if country in lines and 'government' in lines:
            trig = True
            print(lines)
        if trig and '<lifetimes>' in lines:
            start = linenum
            break

    # go through the lines and change lifetime until
    # it hits the end of lifetime definition
    for linenum, lines in enumerate(file_lines[start+1:]):
        if '</lifetimes>' in lines:
            break
        elif ('<val>%i</val>' %orig_lifetime in lines):
            # this is where we add the random
            lifetime_extension = abs(int(np.random.uniform(low, high)))
            lifetime = orig_lifetime + lifetime_extension * 12
            new_lines[start + linenum + 1] = '<val>%i</val>\n' %lifetime

    # write the modified lines into new file
    for line in new_lines:
        new_file.write(line)

    new_file.close()
    default_file.close()
