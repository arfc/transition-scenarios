import sys
import jinja2
import numpy as np
import os

# tells command format if input is invalid
if len(sys.argv) < 6:
    print('Usage: python write_reactors.py [csv] [reactor_template] [region_template]\
        [input_template] [reactor_output] [region_output]')


def delete_file(file):
    """Deletes a file if it exists.

    Parameters
    ----------
    file: str
        filename to delete, if it exists

    Returns
    -------
    null

    """
    if os.path.exists('./' + file) is True:
        os.system('rm ' + file)


def read_csv(csv_file):
    """This function reads the csv file and returns the array.

    Paramters
    ---------
    csv_file: str
        csv file that lists country, reactor name,
        capacity, #assem per core, # assem per batch.

    Returns
    -------
    reactor_lists:  array
        array with the data from csv file
    
    """

    reactor_lists = np.genfromtxt(csv_file,
                                  delimiter=',',
                                  dtype=('S128', 'S128', 'int', 'int', 'int'),
                                  names=('country', 'reactor_name', 'capacity',
                                         'n_assem_core', 'n_assem_batch'))

    return reactor_lists


def read_template(template):
    """ Returns a jinja template
    
    Paramters
    ---------
    template: str
        template file that is to be stored as variable.

    Returns
    -------
    output_template: jinja template object
        output template that can be 'jinja.render' -ed.

    """

    # takes second argument file as reactor template
    with open(template, 'r') as fp:
        input_template = fp.read()
        output_template = jinja2.Template(input_template)

    return output_template


def reactor_render(array, template, output_file):
    """Takes the array and template and writes a reactor file

    Paramters
    ---------
    array: array
        array of data on reactors
    template: jinja.template
        jinja template for reactor file
    output_file: str
        name of output file

    Returns
    -------
    The reactor section of cyclus input file

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


def input_render(reactor_file, region_file, template, output_file):
    """Creates total input file from region and reactor file

    Paramters
    ---------
    reactor_file: str
        jinja rendered reactor section of cyclus input file
    region_file: str
        jinja rendered region section of cylcus input file
    template: str
        jinja template for cyclus complete input file
    output_file: str
        name of output file

    Returns
    -------
    A complete cylus input file.

    """
    with open(reactor_file, 'r') as fp:
        reactor = fp.read()
    with open(region_file, 'r') as bae:
        region = bae.read()

    temp = template.render(reactor_input=reactor, region_input=region)

    with open(output_file, 'a') as output:
        output.write(temp)


def region_render(array, template, full_template, output_file):
    """Takes the array and template and writes a region file
    
    Paramters
    ---------
    array: array
        array of data on reactors
    template: jinja.template
        jinja template for one region prototype declaration
    full_template: jinja.template
        jinja template for full region section file
    output_file: str
        name of output file

    Returns
    -------
    The region section of cyclus input file

    """

    # list of countries
    country_list = []

    # create array of countries and create files for each country.
    for data in array:
        country_list.append(data['country'].decode('utf-8'))
        region_body = \
            template.render(reactor_name=data['reactor_name'].decode('utf-8'))
        with open(data['country'].decode('utf-8'), 'a') as output:
            output.write(region_body)

    # add all the separate region files together, with proper region format
    country_set = set(country_list)
    for country in country_set:

        # jinja render region template for different countries
        with open(country, 'r') as ab:
            country_input = ab.read()
            country_body = full_template.render(country=country,
                                                country_gov=country + '_government',
                                                region_file=country_input)

        # write rendered template as 'country'_region
        with open(country + '_region', 'a') as output:
            output.write(country_body)

        # concatenate the made file to the final output file and remove temp
        os.system('cat ' + country + '_region >> ' + output_file)
        os.system('rm ' + country)
        os.system('rm ' + country + '_region')


def write_reactors(csv_file, reactor_template, region_template,
                   input_template, reactor_output, region_output):
    """ Generates cyclus input file from csv files and jinja templates.

    Paramters
    ---------
    csv_file : str
        csv file containing reactor data (country, name, capacity)
    reactor_template: str
        template file for reactor section of input file
    region_template: str
        template file for region section of input file
    input_template: str
        template file for entire complete cyclus input file
    reactor_output: str
        name of output of reactor section of cyclus input file
    region_output: str
        name of output of region section of cyclus input file

    Returns
    -------
    File with reactor section of cyclus input file
    File with region section of cyclus input file
    File with complete cyclus input file

    """

    # deletes previously existing files
    delete_file('complete_input.xml')
    delete_file(reactor_output)
    delete_file(region_output)

    # read csv and templates
    dataset = read_csv(csv_file)
    input_template = read_template(input_template)
    reactor_template = read_template(reactor_template)
    region_template = read_template(region_template)
    region_output_template = read_template('region_output_template.xml.in')

    # renders reactor / region / input file. Confesses imperfection.
    reactor_render(dataset, reactor_template, reactor_output)
    region_render(dataset, region_template, region_output_template, region_output)
    input_render(reactor_output, region_output, input_template, 'complete_input.xml')
    print('\n Insert sink and source into the regions - updates to come! :) \n ')


if __name__ == "__main__":
    write_reactors(sys.argv[1], sys.argv[2], sys.argv[3],
                   sys.argv[4], sys.argv[5], sys.argv[6])
