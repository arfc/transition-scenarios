import sys
import jinja2
import numpy as np
import os

# tells command format if input is invalid
if len(sys.argv) < 3:
    print('Usage: python write_reactors.py [csv] [reactor_template] [region_template]\
         [reactor_output] [region_output]')

def write_reactors(csv_file, reactor_template, region_template, reactor_output, region_output):
    """ 
    This script allows generation of cyclus input file types from csv files.
    Input : csv file, template for reactor input, template for region
    Output : two input file blocks (reactor and region) for cyclus simulation.

    Usage: 'python write_reactors.py [csv] [reactor_template] [region_template]
                [reactor_output] [region_output]'
    """

    reactor_lists= np.genfromtxt(csv_file,
                                delimiter=',',
                                dtype=('S128','S128', 'int','int', 'int'),
                                names=('country','reactor_name', 'capacity',
                                       'n_assem_core','n_assem_batch'))

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

    # list of countries
    country_list=[]

    # ((region template)) render
    for reactor in reactor_lists:
        country_name= reactor['country'].decode('utf-8')
        country_list.append(country_name)
        region_body= \
        template2.render(reactor_name=reactor['reactor_name'].decode('utf-8'))
        with open(country_name,'a') as output:
            output.write(region_body)

    # add all the separate region files together, with proper region format
    country_set=set(country_list)
    for country in country_set:
        # add region_head and region_tail to country region file
        os.system('cat region_head.xml.in' +" "+ country 
                  + " " + 'region_tail.xml.in >' " "+ country +'_region')
        os.system('cat '+ country +'_region >> ' + region_output)

        # replace SingleRegion and SingleInstitution with country and gov
        os.system("sed -i 's/SingleRegion/" + country + "/g' " + region_output)
        os.system("sed -i 's/SingleInstitution/" + country
                  + "_government /g' " + region_output)
        os.system('rm '+country)
        os.system('rm '+country+ '_region')

##end of write_reactors

#calls function write_reactors
write_reactors(sys.argv[1], sys.argv[2],
               sys.argv[3], sys.argv[4], sys.argv[5])