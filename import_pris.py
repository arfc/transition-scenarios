import csv
import dateutil.parser as date
import import_fleetcomp as idata
import jinja2
import numpy as np
import os
import pathlib
import sys

if len(sys.argv) < 4:
    print('Usage: python import_pris.py [region] [sim_start_yr]')


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
        country = row[0]
        if country.upper() in regions[region.upper()]:
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
        delta = ((start_date[0] - int(start_year)) * 12 +
                 (start_date[1]) +
                 round(start_date[2] / (365.0 / 12)))
        for index, reactor in enumerate(path_list):
            name = row[1].replace(' ', '_')
            country = row[0]
            file_name = (reactor.replace(
                os.path.dirname(path_list[index]), '')).replace('/', '')
            if (name + '.xml' == file_name):
                buildtime_dict.update({name: (country, delta)})
    return buildtime_dict


def write_reactors(in_list, out_path, reactor_template):
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
    if out_path[-1] != '/':
        out_path += '/'
    pathlib.Path(out_path).mkdir(parents=True, exist_ok=True)
    for row in in_list:
        capacity = float(row[3])
        if capacity >= 400:
            name = row[1].replace(' ', '')
            assem_per_batch = 0
            assem_no = 0
            assem_size = 0
            reactor_type = row[2]
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
                                               power_cap=row[3])
            with open(out_path + name.replace(' ', '_') + '.xml',
                      'w') as output:
                output.write(rendered)


def write_deployment(in_dict, out_path, deployinst_template,
                     inclusions_template):
    """ Renders jinja template using dictionary of reactor name and buildtime
    and outputs an xml file that uses xinclude to include the reactors located
    in cyclus_input/reactors.

    Parameters
    ---------
    in_dict: dictionary
        dictionary with key: reactor name, and value: buildtime.
    out_path: str
        output path for files
    deployinst_template: jinja template object
        jinja template object to be rendered with deployinst.
    inclusions_template: jinja template object
        jinja template object to be rendered with reactor inclusions.

    Returns
    -------
    null
        generates single xml file that includes reactors specified in
        the dictionary.
    """
    if out_path[-1] != '/':
        out_path += '/'
    pathlib.Path(out_path).mkdir(parents=True, exist_ok=True)
    country_list = {value[0] for value in in_dict.values()}
    for nation in country_list:
        temp_dict = {}
        for reactor in in_dict.keys():
            if in_dict[reactor][0] == nation:
                temp_dict.update({reactor: in_dict[reactor][1]})
        print(temp_dict)
        pathlib.Path(out_path + nation +
                     '/').mkdir(parents=True, exist_ok=True)
        deployinst = deployinst_template.render(reactors=temp_dict)
        with open(out_path + nation + '/deployinst.xml', 'w') as output1:
            output1.write(deployinst)
    inclusions = inclusions_template.render(reactors=in_dict)
    with open(out_path + 'inclusions.xml', 'w') as output2:
        output2.write(inclusions)


def obtain_reactors(in_csv, region, reactor_template):
    """ Writes xml files for individual reactors in US fleet.

    Parameters
    ----------
    in_csv: str
        csv file name.
    reactor_template: str
        template file name.
    region: str
        region name

    Returns
    -------
    null
        Writes xml files for individual reactors in US fleet.
    """
    in_data = idata.import_csv(in_csv, ',')
    reactor_list = select_region(in_data, region)
    reactor_tmpl = idata.load_template(reactor_template)
    out_path = 'cyclus/input/' + region + '/reactors'
    write_reactors(reactor_list, out_path, reactor_tmpl)


def deploy_reactors(in_csv, region, start_year, deployinst_template,
                    inclusions_template, reactors_path, deployment_path):
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
    if reactors_path[-1] != '/':
        reactors_path += '/'
    for files in os.listdir(reactors_path):
        lists.append(reactors_path + files)
    in_data = idata.import_csv(in_csv, ',')
    reactor_list = select_region(in_data, region)
    buildtime = get_buildtime(reactor_list, start_year, lists)
    write_deployment(buildtime, deployment_path, deployinst_template,
                     inclusions_template)
    return buildtime


def render_cyclus(cyclus_template, in_dict, path, output_name):
    if path[-1] != '/':
        path += '/'
    country_list = {value[0] for value in in_dict.values()}
    cyclus = idata.load_template(cyclus_template)
    rendered = cyclus.render(countries=country_list)
    with open(path + output_name + '.xml', 'w') as output:
        output.write(rendered)


if __name__ == '__main__':
    pris_file = 'import_data/reactors_pris_2016.csv'
    obtain_reactors(pris_file, sys.argv[1], 'templates/reactors_template.xml')
    deployinst_tmpl = 'templates/' + sys.argv[1] + '/deployinst_template.xml'
    inclusions_tmpl = 'templates/inclusions_template.xml'
    cyclus_tmpl = (
        'templates/' + sys.argv[1] + '/' + sys.argv[1] + '_template.xml')
    reactor_path = 'cyclus/input/' + sys.argv[1] + '/reactors'
    dployment_path = 'cyclus/input/' + sys.argv[1] + '/buildtimes'
    buildtime = deploy_reactors(pris_file,
                                sys.argv[1], sys.argv[2],
                                idata.load_template(deployinst_tmpl),
                                idata.load_template(inclusions_tmpl),
                                reactor_path, dployment_path)
    render_cyclus(cyclus_tmpl, buildtime, 'cyclus/input/', sys.argv[1])
