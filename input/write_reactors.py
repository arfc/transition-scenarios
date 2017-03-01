import sys
import jinja2
import numpy as np
import os

# tells command format if input is invalid
#if len(sys.argv) < 5:
#   print('Usage: python write_reactors.py [csv] [reactor_template] [region_template]\
#        [reactor_output] [region_output]')

def write_reactors (csv_file, reactor_template, region_template, reactor_output, region_output):
    """ 
    This script allows generation of cyclus input file types from csv files.
    Input : csv file, template for reactor input, template for region
    Output : two input file blocks (reactor and region) for cyclus simulation.

    csv_file: the csv file containing reactor name, capacity and the appropriate
              number of assemblies per core and per batch
    reator_template: input file name for jinja template for cyclus reactor input
    region_template: input file name for jinja template for cyclus region input
    ractor_output: output file name for cyclus reactor input file
    region_output: output file name for cyclus region input file

    """

def read_csv(csv_file):
    """
    This function reads the csv file and returns the array.

    input) 
        csv_file: csv file that lists country, reactor name,
                 capacity, #assem per core, # assem per batch.

    return)
        reactor_lists: array with the data from csv file
    """

    reactor_lists= np.genfromtxt(csv_file,
                                delimiter=',',
                                dtype=('S128','S128', 'int','int', 'int'),
                                names=('country','reactor_name', 'capacity',
                                       'n_assem_core','n_assem_batch'))

    return reactor_lists


def read_template (template):
    """
    This function takes a jinja template file and returns it

    input)
        template: jinja template file

    return)
        jinja template object
    """
    # takes second argument file as reactor template
    with open(template, 'r') as fp:
        input_template = fp.read()
        output_template = jinja2.Template(input_template) 

    return output_template



def reactor_render (array, template, output_file):
    """
    This function takes the array and template and writes a reactor file

    input)
        array: array of information on reactors
        template: jinja template for reactor file
        output_file: name of the output file

    output)
        completed reactor agent input file for cylcus
    """
    for data in array:
        reactor_body = \
        template.render(country=data['country'].decode('utf-8'),
                        reactor_name=data['reactor_name'].decode('utf-8'),
                        n_assem_core=data['n_assem_core'],
                        n_assem_batch=data['n_assem_batch'],
                        capacity=data['capacity'])
        with open(output_file, 'a') as output:
            output.write(reactor_body)

def region_render (array, template, output_file):
    """
    This function takes the array and template and writes a region file

    input)
        array: array of information on reactors
        template: jinja template for region file
        output_file: name of the output file

    output)
        completed region input file section for cyclus
    """
    
    # list of countries
    country_list=[]

    #create array of countries and create files for each country.
    for data in array:
        country_list.append(data['country'].decode('utf-8'))
        region_body= \
        template.render(reactor_name=data['reactor_name'].decode('utf-8'))
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

## end of write_reactors

# calls function write_reactors
#if __name__ == "__main__":
#    write_reactors(sys.argv[1], sys.argv[2], sys.argv[3],
#                   sys.argv[4], sys.argv[5])
