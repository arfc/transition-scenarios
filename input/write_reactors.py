import sys
import jinja2
import numpy as np
import os

# tells command format if input is invalid
if len(sys.argv) < 6:
    print('Usage: python write_reactors.py [csv] [reactor_template] [deployinst_template]\
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

    reactor_lists = np.genfromtxt(csv_file, skip_header = 1,
                                  delimiter=',',
                                  dtype=('S128', 'S128', 'S128', 'int', 
                                         'int', 'int', 'S128',
                                         'S128', 'int', 'int', 'int',
                                         'int', 'int', 'int',
                                         'int', 'int', 'float'),
                                  names=('country', 'reactor_name', 'type', 'capacity',
                                         'n_assem_core', 'n_assem_batch','status',
                                         'operator', 'const_date', 'cons_year', 'first_crit',
                                         'entry_time', 'lifetime', 'first_grid',
                                         'commercial', 'shutdown_date', 'ucf'))

    return reactor_lists

def get_ymd(yyyymmdd):
    """This function extracts year and month value from yyyymmdd format
        
        The month value is rounded up if the day is above 16

    Prameters
    ---------
    yyyymmdd: int
        date in yyyymmdd format

    Returns
    -------
    year: int
        year
    month: int
        month
    """

    year = yyyymmdd // 10000
    month = (yyyymmdd // 100) % 100
    day = yyyymmdd % 10000
    if day > 16:
        month += 1
    return (year, month)

def get_lifetime(start_date, end_date):
    """This function gets the lifetime for a prototype given the
       start and end date.

    Prameters
    ---------
    start_date: int
        start date of reactor - first criticality.
    end_date: int
        end date of reactor - null if not listed or unknown

    Returns
    -------
    lifetime: int
        lifetime of the prototype in months

    """

    if end_date != -1:
        end_year, end_month = get_ymd(end_date)
        start_year, start_month = get_ymd(start_date)
        dyear = end_year - start_year
        dmonth = end_month - start_month
        if dmonth<0:
            dyear -= 1
            start_month += 12
        dmonth = end_month - start_month

        return (12 * dyear + dmonth)
    else:
        return 720

def get_entrytime(init_date, start_date):
    """This function converts the date format and saves it in variables.

        All dates are in format - yyyymmdd

    Prameters
    ---------
    init_date: int
        start date of simulation
    start_date: int
        start date of reactor - first criticality.
    
    Returns
    -------
    entry_time: int
        timestep of the prototype to enter
    
    """

    init_year, init_month = get_ymd(init_date)
    start_year, start_month = get_ymd(start_date)
    
    dyear = start_year-init_year
    dmonth = start_month - init_month
    if dmonth<0:
        dyear -= 1
        start_month += 12
    dmonth = start_month - init_month

    entry_time = 12 * dyear + dmonth

    if entry_time < 0:
        lifetime = lifetime + entry_time
        if lifetime < 0:
            lifetime = 0
        entry_time = 0
    
    return entry_time
    

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


def input_render(init_date, reactor_file, region_file, template, output_file):
    """Creates total input file from region and reactor file

    Paramters
    ---------
    init_date: int
        date of desired start of simulation (format yyyymmdd)
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
    startmonth = (init_date // 100) % 100
    startyear = init_date // 10000

    temp = template.render(startmonth = startmonth, startyear = startyear,
                           reactor_input=reactor, region_input=region)

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

    country_list = []
    empty_country =[]

    valhead = '<val>'
    valtail = '</val>'

    # creates list of countries and turns it into a set
    for data in array:
        country_list.append(data['country'].decode('utf-8'))
    country_set = set(country_list)

    for country in country_set:
        prototype = ''
        entry_time = ''
        number = ''
        lifetime = ''

        for data in array:
            if (data['country'].decode('utf-8') == country and data['entry_time'] != 0):
                prototype += valhead + data['reactor_name'].decode('utf-8') +valtail + '\n'
                entry_time += valhead + str(data['entry_time']) +valtail + '\n'
                number += valhead + '1' + valtail +'\n'
                lifetime += valhead + str(data['lifetime']) +valtail + '\n'
     
        render_temp = template.render(prototype = prototype,
                                      start_time = entry_time,
                                      number = number,
                                      lifetime = lifetime)
        if len(render_temp) > 110:
            with open(country, 'a') as output:
                output.write(render_temp)
        else:
            empty_country.append(country)

    for country in empty_country:
        country_set.remove(country)
       

    # create array of countries and create files for each country.
    for country in country_set:
        # jinja render region template for different countries
        with open(country, 'r') as ab:
            country_input = ab.read()
            country_body = full_template.render(country=country,
                                                country_gov=country + '_government',
                                                deployinst = country_input)

        # write rendered template as 'country'_region
        with open(country + '_region', 'a') as output:
            output.write(country_body)

        # concatenate the made file to the final output file and remove temp
        os.system('cat ' + country + '_region >> ' + output_file)
        os.system('rm ' + country)
        os.system('rm ' + country + '_region')


def main(csv_file, reactor_template, deployinst_template,
         input_template, reactor_output, region_output):
    """ Generates cyclus input file from csv files and jinja templates.

    Paramters
    ---------
    csv_file : str
        csv file containing reactor data (country, name, capacity)
    reactor_template: str
        template file for reactor section of input file
    deployinst_template: str
        template file for deployinst section of input file
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

    #initialize initial values form (yyyymmdd)
    init_date = 19400101


    # read csv and templates
    dataset = read_csv(csv_file)
    input_template = read_template(input_template)
    reactor_template = read_template(reactor_template)
    region_output_template = read_template('region_output_template.xml.in')
    deployinst_template = read_template('deployinst_template.xml.in')

    for data in dataset:
        entry_time = get_entrytime(init_date, data['first_crit'])
        lifetime = get_lifetime(data['first_crit'], data['shutdown_date'])
        data['entry_time'] = entry_time
        data['lifetime'] = lifetime       
    # renders reactor / region / input file. Confesses imperfection.
    reactor_render(dataset, reactor_template, reactor_output)
    region_render(dataset, deployinst_template, region_output_template, region_output)
    input_render(init_date, reactor_output, region_output, input_template, 'complete_input.xml')
    print('\n Insert sink and source into the regions - updates to come! :) \n ')


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3],
         sys.argv[4], sys.argv[5], sys.argv[6])
