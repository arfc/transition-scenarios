import sys
import jinja2
import numpy as np

if len(sys.argv) < 3:
    print('Usage: python write_reactors.py [csv] [reactor_template] [region_template] [reactor_output] [region_output]')

def write_reactors(csv_file, reactor_template, region_template, reactor_output, region_output):
    """ 
    This script allows generation of cyclus input file types from csv files.
    Args:
        csv_file: the csv file containing reactor name, capacity,
                  and appropriate number of assemblies per core and per batch
        reactor_template: input file name for jinja template for cyclus reactor input
        region_template: input file name for jinja template for cyclus region input
        reactor_output: output file name for cyclus reactor input file
        region_output: output file name for cyclus region input file

    Output : two input file blocks (reactor and region) for cyclus simulation.
    """

    # display usage if in error
    if len(sys.argv) <3:
        print("Usage: 'Python write_reactors.py [csv] [reactor_template] [region_template]\
             [reactor_output] [region_output]")

    reactor_lists= np.genfromtxt(csv_file,
    	                        delimiter=',',
    	                        dtype=('S128','S128', 'int','int', 'int'),
                                names=('country','reactor_name', 'capacity','n_assem_core',
                                       'n_assem_batch'))

    # takes second argument file as reactor template
    with open(reactor_template, 'r') as fp:
        input_template = fp.read()
        template = jinja2.Template(input_template) 

    # takes third argument file as region template
    with open(region_template,'r') as ft:
	    input_template2 = ft.read()
	    template2 = jinja2.Template(input_template2)

    # ((reactor template)) render
    for reactor in reactor_lists:
        reactor_body = \
        template.render(country=reactor['country'].decode('utf-8'),
    	                reactor_name=reactor['reactor_name'].decode('utf-8'),
                        n_assem_core=reactor['n_assem_core'],
                        n_assem_batch=reactor['n_assem_batch'],
                        capacity=reactor['capacity'])
        with open(reactor_output, 'a') as output:
            output.write(reactor_body)

    # ((region template)) render
    for reactor in reactor_lists:
	    region_body= \
	    template2.render(country=reactor['country'].decode('utf-8'),
		                 reactor_name=reactor['reactor_name'].decode('utf-8'))
	    with open(region_output,'a') as output:
		    output.write(region_body)

##end of write_reactors

#calls function write_reactors
write_reactors(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
