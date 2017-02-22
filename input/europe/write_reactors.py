import sys
import jinja2
import numpy as np

# to run:
if len(sys.argv) < 3:
    print('Usage: python write_reactors.py [csv] [template1] [template2] [output1] [output2]')

# loads reactor info
reactor_lists = np.genfromtxt(sys.argv[1],
                              delimiter=',',
                              dtype=('S128','S128', 'int', 'int'),
                              names=('country','reactor_name', 'n_assem_core',
                                     'n_assem_batch'))

# takes second argument file as template
with open(sys.argv[2], 'r') as fp:
    input_template = fp.read()
    template = jinja2.Template(input_template)

#takes third argument file as region template
with open(sys.argv[3],'r') as ft:
	input_template2 = ft.read()
	template2 = jinja2.Template(input_template2)

# for every row, replace the following items with values in the csv file.
for reactor in reactor_lists:
    reactor_body = \
    template.render(country=reactor['country'].decode('utf-8'),
    	            reactor_name=reactor['reactor_name'].decode('utf-8'),
                    n_assem_core=reactor['n_assem_core'],
                    n_assem_batch=reactor['n_assem_batch'])
    with open(sys.argv[4], 'a') as output:
        output.write(reactor_body)

# ((region template)) render
for reactor in reactor_lists:
	region_body= \
	template2.render(country=reactor['country'].decode('utf-8'),
		             reactor_name=reactor['reactor_name'].decode('utf-8'))
	with open(sys.argv[5],'a') as output:
		output.write(region_body)
