import sys
import jinja2
import numpy as np
import os

# tells command format if input is invalid
if len(sys.argv) < 3:
    print('Usage: python write_reactors.py [csv]' +
          '[init_date] [duration]')


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
    """This function reads the csv file and returns the list.

    Parameters
    ---------
    csv_file: str
        csv file that lists country, reactor name,
        capacity, #assem per core, # assem per batch.

    Returns
    -------
    reactor_lists:  list
        list with the data from csv file

    """

    reactor_lists = np.genfromtxt(csv_file,
                                  skip_header=1,
                                  delimiter=',',
                                  dtype=('S128', 'S128',
                                         'S128', 'int',
                                         'S128', 'S128', 'int',
                                         'int', 'int',
                                         'int', 'int',
                                         'int', 'int',
                                         'int', 'float'),
                                  names=('country', 'reactor_name',
                                         'type', 'capacity',
                                         'status', 'operator', 'const_date',
                                         'cons_year', 'first_crit',
                                         'entry_time', 'lifetime',
                                         'first_grid', 'commercial',
                                         'shutdown_date', 'ucf'))
    # deletes experimental reactors (reactors with capacity < 100 MWe)
    hitlist = []
    count = 0
    for data in reactor_lists:
        if data['capacity'] < 100:
            hitlist.append(count)
        count += 1
    reactor_lists = np.delete(reactor_lists, hitlist)

    return reactor_lists


def get_ymd(yyyymmdd):
    """This function extracts year and month value from yyyymmdd format

        The month value is rounded up if the day is above 16

    Parameters
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
    day = yyyymmdd % 100
    if day > 16:
        month += 1
    return (year, month)


def get_lifetime(start_date, end_date):
    """This function gets the lifetime for a prototype given the
       start and end date.

    Parameters
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
        if dmonth < 0:
            dyear -= 1
            start_month += 12
        dmonth = end_month - start_month

        return (12 * dyear + dmonth)
    else:
        return 720


def get_entrytime(init_date, start_date):
    """This function converts the date format and saves it in variables.

        All dates are in format - yyyymmdd

    Parameters
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
    if dmonth < 0:
        dyear -= 1
        start_month += 12
    dmonth = start_month - init_month

    entry_time = 12 * dyear + dmonth

    return entry_time


def read_template(template):
    """ Returns a jinja template

    Parameters
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


def reactor_render(list, template, mox_template, output_file):
    """Takes the list and template and writes a reactor file

    Parameters
    ---------
    list: list
        list of data on reactors
    template: jinja.template
        jinja template for reactor file
    mox_template: jinja.template
        jinja template for mox reactor file
    output_file: str
        name of output file

    Returns
    -------
    The reactor section of cyclus input file

    """

    for data in list:
        # BWRs have different fuel assembly size, assembly per core and batch
        if data['type'].decode('utf-8') == 'BWR':
            reactor_body = template.render(
                                           country=data['country'].decode('utf-8'),
                                           reactor_name=data['reactor_name'].decode('utf-8'),
                                           assem_size=180,
                                           n_assem_core=int(round(data['capacity']/1000 * 764)),
                                           n_assem_batch=int(round(data['capacity']/3000 * 764)),
                                           capacity=data['capacity'])
        # if French PWR, use mox template for mox reactor
        elif data['type'].decode('utf-8') == 'PWR' and data['country'].decode('utf-8') == 'France':
            reactor_body = mox_template.render(country=data['country'].decode('utf-8'),
                                               reactor_name=data['reactor_name'].decode('utf-8'),
                                               assem_size=523.4,
                                               n_assem_core=int(round(data['capacity']/1000 * 193)),
                                               n_assem_batch=int(round(data['capacity']/3000 * 193)),
                                               capacity=data['capacity'])
        # if not BWRS, all go with PWR specification.
        else:
            reactor_body = template.render(
                                           country=data['country'].decode('utf-8'),
                                           reactor_name=data['reactor_name'].decode('utf-8'),
                                           assem_size=523.4,
                                           n_assem_core=int(round(data['capacity']/1000 * 193)),
                                           n_assem_batch=int(round(data['capacity']/3000 * 193)),
                                           capacity=data['capacity'])
        with open(output_file, 'a') as output:
            output.write(reactor_body)


def input_render(init_date, duration, reactor_file,
                 region_file, template, output_file, reprocessing):
    """Creates total input file from region and reactor file

    Parameters
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
    reprocessing: bool
        True if reprocessing is done, false if ignored

    Returns
    -------
    A complete cylus input file.

    """
    with open(reactor_file, 'r') as fp:
        reactor = fp.read()
    with open(region_file, 'r') as bae:
        region = bae.read()

    startyear, startmonth = get_ymd(init_date)

    # has reprocessing chunk if reprocssing boolean is true.
    if reprocessing is True:
        reprocessing_chunk = ('<entry>\n'
                              + '  <number>1</number>\n'
                              + '  <prototype>reprocessing</prototype>\n'
                              + '</entry>')
    else:
        reprocessing_chunk = ''

    # renders template
    temp = template.render(duration=duration,
                           startmonth=startmonth,
                           startyear=startyear,
                           reprocessing=reprocessing_chunk,
                           reactor_input=reactor,
                           region_input=region)

    with open(output_file, 'w') as output:
        output.write(temp)

    os.system('rm reactor_output.xml.in region_output.xml.in')


def region_render(list, template, full_template, output_file):
    """Takes the list and template and writes a region file

    Parameters
    ---------
    list: list
        list of data on reactors
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
    empty_country = []

    valhead = '<val>'
    valtail = '</val>'

    # creates list of countries and turns it into a set
    for data in list:
        country_list.append(data['country'].decode('utf-8'))
    country_set = set(country_list)

    for country in country_set:
        prototype = ''
        entry_time = ''
        number = ''
        lifetime = ''

        for data in list:
            if data['country'].decode('utf-8') == country:

                prototype += (valhead
                              + data['reactor_name'].decode('utf-8')
                              + valtail + '\n')
                entry_time += (valhead
                               + str(data['entry_time']) + valtail + '\n')
                number += valhead + '1' + valtail + '\n'
                lifetime += valhead + str(data['lifetime']) + valtail + '\n'

        render_temp = template.render(prototype=prototype,
                                      start_time=entry_time,
                                      number=number,
                                      lifetime=lifetime)
        if len(render_temp) > 100:
            with open(country, 'a') as output:
                output.write(render_temp)
        else:
            empty_country.append(country)

    for country in empty_country:
        country_set.remove(country)

    for country in country_set:
        # jinja render region template for different countries
        with open(country, 'r') as ab:
            country_input = ab.read()
            country_body = full_template.render(
                                                country=country,
                                                country_gov=(country
                                                             + '_government'),
                                                deployinst=country_input)

        # write rendered template as 'country'_region
        with open(country + '_region', 'a') as output:
            output.write(country_body)

        # concatenate the made file to the final output file and remove temp
        os.system('cat ' + country + '_region >> ' + output_file)
        os.system('rm ' + country)
        os.system('rm ' + country + '_region')


def main(csv_file, init_date, duration, reactor_template, mox_reactor_template,
         reprocessing, deployinst_template, input_template, output_file):
    """ Generates cyclus input file from csv files and jinja templates.

    Parameters
    ---------
    csv_file : str
        csv file containing reactor data (country, name, capacity)
    init_date: int
        yyyymmdd format of inital date of simulation
    reactor_template: str
        template file for reactor section of input file
    mox_reactor_templtae: str
        template file for mox reactor section of input file
    reprocessing: bool
        True if reprocessing is done, False if not
    deployinst_template: str
        template file for deployinst section of input file
    input_template: str
        template file for entire complete cyclus input file
    output_file: str
        directory and name of complete cyclus input file

    Returns
    -------
    File with reactor section of cyclus input file
    File with region section of cyclus input file
    File with complete cyclus input file

    """

    # deletes previously existing files
    delete_file('complete_input.xml')

    # read csv and templates
    dataset = read_csv(csv_file)
    input_template = read_template(input_template)
    reactor_template = read_template(reactor_template)
    mox_reactor_template = read_template(mox_reactor_template)
    region_output_template = read_template('../templates/'
                                           + 'region_output_template.xml.in')
    deployinst_template = read_template(deployinst_template)

    for data in dataset:
        entry_time = get_entrytime(init_date, data['first_crit'])
        lifetime = get_lifetime(data['first_crit'], data['shutdown_date'])
        if entry_time <= 0:
            lifetime = lifetime + entry_time
            if lifetime < 0:
                lifetime = 0
            entry_time = 1

        data['entry_time'] = entry_time
        data['lifetime'] = lifetime
    # renders reactor / region / input file. Confesses imperfection.
    reactor_render(dataset, reactor_template,
                   mox_reactor_template,
                   'reactor_output.xml.in')
    region_render(dataset, deployinst_template,
                  region_output_template, 'region_output.xml.in')
    input_render(init_date, duration, 'reactor_output.xml.in',
                 'region_output.xml.in',
                 input_template, output_file, reprocessing)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]),
         '../templates/reactor_template.xml.in',
         '../templates/reactor_mox_template.xml.in',
         False,
         '../templates/deployinst_template.xml.in',
         '../templates/input_template.xml.in',
         'complete_input.xml')
