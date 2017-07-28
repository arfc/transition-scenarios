import csv
import dateutil.parser as date
import import_data as idata
import numpy as np
import os


def select_region(in_list, region):
    """ Returns a list of reactors that have a start_date
    and are note experimental

    Parameters
    ----------
    in_list: list
            imported csv file in list format
    region: str
            name of the region

    Returns
    -------
    reactor_list: list
            list of reactors from PRIS
    """
    SOUTH_AMERICA = {'ARGENTINA', 'BRAZIL'}
    NORTH_AMERICA = {'CANADA', 'MEXICO', 'UNITED STATES'}
    EUROPE = {'BELARUS', 'BELGIUM', 'BULGARIA',
              'CZECHOSLOVAKIA', 'FINLAND', 'FRANCE',
              'GERMANY', 'ITALY', 'NETHERLANDS',
              'POLAND', 'ROMANIA', 'RUSSIA',
              'SLOVENIA', 'SOVIET UNION', 'SPAIN',
              'SWEDEN', 'SWITZERLAND', 'TURKEY',
              'UKRAINE', 'UNITED KINGDOM'
              }
    ASIA = {'BANGLADESH', 'CHINA', 'INDIA',
            'IRAN', 'JAPAN', 'KAZAKHSTAN',
            'PAKISTAN', 'PHILIPPINES', 'SOUTH KOREA',
            'UNITED ARAB EMIRATES', 'VIETNAM'}
    AFRICA = {'EGYPT', 'MOROCCO', 'SOUTH AFRICA', 'TUNISIA'}
    ALL = SOUTH_AMERICA | NORTH_AMERICA | EUROPE | ASIA | AFRICA
    regions = {'SOUTH_AMERICA': SOUTH_AMERICA, 'NORTH_AMERICA': NORTH_AMERICA,
               'ASIA': ASIA, 'AFRICA': AFRICA, 'EUROPE': EUROPE, 'ALL': ALL}

    if region.upper() not in regions.keys():
        raise ValueError(region + 'is not a valid region')
    reactor_list = []
    for row in in_list:
        country = in_list[row][0]
        if country in regions[region]:
            start_date = row[9]
            if start_date.strip():
                reactor_list.append(row)
    return reactor_list


def get_lifetime(in_list):
    """ Calculates the lifetime of a reactor using first
    grid data and shutdown date. Defaults to 720 if these
    data are not available

    Parameters
    ----------
    in_list: list
        single row from PRIS data that contains reactor 
        information

    Returns
    -------
    lifetime: int
        lifetime of reactor
    """
    grid_date = in_list[9]
    shutdown_date = in_list[11]
    if not shutdown_date.strip():
        return 720
    else:
        n_days_month = 365.0 / 12
        delta = (date.parse(shutdown_date) - date.parse(grid_date)).days
        return int(delta / n_days_month)


def get_buildtime(in_list, start_year, path_list):
    """ Obtains infroation regarding reactors that need to
    be deployed and renders the information into a jinja
    template

    Parameters
    ----------
    in_list: list
        list of reactors
    start_year: int
        starting year of simulation
    path_list: list
        list of paths to reactor files

    Returns
    -------
    null
    """
    buildtime_dict = {}
    for row in in_list:
        grid_date = date.parse(row[9])
        start_date = [grid_date.year, grid_date.month, grid_date.day]
        delta = ((start_date[0] - start_year) * 12 +
                 (start_date[1]) +
                 round(start_date[2] / (365.0 / 12)))
        for index, reactor in enumerate(path_list):
            name = row[0].replace(' ', '')
            file_name = (reactor.replace(
                os.path.dirname(path_list[index]), '')).replace('/', '')
            if (name + '.xml' == file_name):
                buildtime_dict.update({name: delta})
    return buildtime_dict


def write_reactors(in_list, reactor_template):
    """ Obtains information regarding reactors
    and renders the information into a jinja template

    Parameters
    ----------
    in_list: list
            list containing PRIS data
    reactor_template: jinja template object
            jinja template object to be rendered.

    Returns
    -------
    null
    """
    for row in in_list:
        capacity = float(in_list[row][3])
        if capacity >= 400:
            name = row[0].replace(' ', '')
            assem_per_batch = 0
            assem_no = 0
            assem_size = 0
            reactor_type = in_list[row][2]
            if reactor_type == 'BWR':
                assem_no = 732
                assem_per_batch = assem_no / 3
                assem_size = 150
            else:
                assem_no = 240
                assem_per_batch = assem_no / 3
                assem_size = 417
            rendered = reactor_template.render(name=name,
                                               lifetime=get_lifetime(row),
                                               assem_size=assem_size,
                                               n_assem_core=assem_no,
                                               n_assem_batch=assem_per_batch,
                                               power_cap=in_list[row][3])
            with open('cyclus/input/europe_test/reactors/' +
                      name.replace(' ', '_') +
                      '.xml', 'w') as output:
                output.write(rendered)


def obtain_reactors(in_csv, reactor_template):
    """ Writes xml files for individual reactors in US fleet.

    Parameters
    ---------
    in_csv: str
        csv file name.
    reactor_template: str
        template file name.

    Returns
    -------
    null
        Writes xml files for individual reactors in US fleet.
    """


def deploy_reactors(in_csv, deployinst_template, inclusions_template, path):
    """ Generates xml files that specifies the reactors that will be included
    in a cyclus simulation.

    Parameters
    ---------
    in_csv: str
        csv file name.
    deployinst_template: jinja template object
        jinja template object to be rendered with deployinst.
    inclusions_template: jinja template object
        jinja template object to be rendered with reactor inclusions.
    *args: str
        path and name of reactors that will be added to cyclus simulation.

    Returns
    -------
    null
        generates single xml file that includes reactors specified in
        the dictionary.
    """
    lists = []
    if path[-1] != '/':
        path += '/'
    for files in os.listdir(path):
        lists.append(path + files)
