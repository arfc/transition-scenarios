import sys
import jinja2
import numpy as np

# to run:
if len(sys.argv) < 3:
    print('Usage: ./write_reactors.py france.csv template.xml.in france_input.xml')

# loads reactor info
reactor_lists = np.genfromtxt(sys.argv[1],
                              delimiter=',',
                              dtype=('S128', 'float64', 'float64'),
                              names=('reactor_name', 'n_assem_core',
                                     'n_assem_batch'))

# takes second argument file as template
with open(sys.argv[2], 'r') as fp:
    input_template = fp.read()
    template = jinja2.Template(input_template)

# for every row, replace the following items with values in the csv file.
for reactor in reactor_lists:
    reactor_body = \
    template.render(reactor_name=reactor['reactor_name'].decode('utf-8'),
                    n_assem_core=reactor['n_assem_core'],
                    n_assem_batch=reactor['n_assem_batch'])
    with open(sys.argv[3], 'a') as output:
        output.write(reactor_body)
