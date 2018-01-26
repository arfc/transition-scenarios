import csv
import dateutil.parser as date
import jinja2
import numpy as np
import os
import pathlib
import sqlite3 as sql
import sys
from fuzzywuzzy import fuzz
from pyne import nucname as nn

if len(sys.argv) < 4:
    print('Usage: python import_pris.py [region] [sim_start_yr]')


def get_cursor(file_name):
    """ Connects and returns a cursor to an sqlite output file

    Parameters
    ----------
    file_name: str
        name of the sqlite file

    Returns
    -------
    sqlite cursor3
    """
    con = sql.connect(file_name)
    con.row_factory = sql.Row
    return con.cursor()


def merge_coordinates(pris_link, scrape):
    """ Obtains coordinates from webscrape.sqlite and
    writes them to matching reactors in PRIS reactor file.

    Parameters
    ----------
    pris_link: str
        path and name of pris reactor text file
    scrape: str
        path and name of webscrape sqlite file

    Returns
    -------
    null
        Writes pris text file with coordinates
    """
    pris = []
    others = {'OHI-': 'Ōi',
              'ASCO-': 'Ascó',
              'ROVNO-': 'Rivne',
              'SHIN-KORI-': 'Kori',
              'ANO-': 'Arkansas One',
              'HANBIT-': 'Yeonggwang',
              'FERMI-': 'Enrico Fermi',
              'BALTIC-': 'Kaliningrad',
              'COOK-': 'Donald C. Cook',
              'HATCH-': 'Edwin I. Hatch',
              'HARRIS-': 'Shearon Harris',
              'SHIN-WOLSONG-': 'Wolseong',
              'ST. ALBAN-': 'Saint-Alban',
              'LASALLE-': 'LaSalle County',
              'SUMMER-': 'Virgil C. Summer',
              'FARLEY-': 'Joseph M. Farley',
              'ST. LAURENT ': 'Saint-Laurent',
              'HADDAM NECK': 'Connecticut1 Yankee',
              'HIGASHI DORI-1 (TOHOKU)': 'Higashidōri',
              }
    blacklist = ['nuclear', 'power',
                 'plant', 'generating',
                 'station', 'reactor', 'atomic',
                 'energy', 'center', 'electric']
    with open(pris_link, encoding='utf-8') as src:
        reader = csv.reader(src, delimiter=',')
        pris.extend(reader)
        cur = get_cursor(scrape)
        coords = cur.execute(
            "SELECT name, long, lat FROM reactors_coordinates")
        for web in coords:
            for prs in pris[1:]:
                name_web = web['name'].lower()
                for blacklisted in blacklist:
                    name_web = name_web.replace(blacklisted, '')
                if fuzz.ratio(name_web.rstrip(), prs[1].lower()) > 64:
                    # print(name_web.rstrip(), ' and ', prs[1].lower())
                    prs[13] = web['lat']
                    prs[14] = web['long']
                else:
                    for other in others.keys():
                        if fuzz.ratio(prs[1].lower(), other.lower()) > 80:
                            if fuzz.ratio(others[other].lower(),
                                          name_web.rstrip().lower()) > 75:
                                # print(prs[1], ' and ', name_web.rstrip())
                                prs[13] = web['lat']
                                prs[14] = web['long']
    with open('reactors_pris_2016.csv', 'w') as output:
        writer = csv.writer(output, delimiter=',')
        writer.writerows(pris)


def import_csv(in_csv, delimit):
    """ Imports contents of a csv text file to a list of
    lists.

    Parameters
    ---------
    in_csv: str
        path and name of input csv file
    delimit: str
        delimiter of the csv file

    Returns
    -------
    data_list: list
        list of lists containing the csv data
    """
    with open(in_csv, encoding='utf-8') as source:
        sourcereader = csv.reader(source, delimiter=delimit)
        data_list = []
        for row in sourcereader:
            data_list.append(row)
    return data_list


def load_template(in_template):
    """ Returns a jinja2 template from file.

    Parameters
    ---------
    in_template: str
        path and name of jinja2 template

    Returns
    -------
    output_template: jinja template object
    """
    with open(in_template, 'r') as default:
        output_template = jinja2.Template(default.read())
    return output_template


def get_composition_fresh(in_list, burnup):
    """ Returns a dictionary of isotope and composition (in mass fraction)
    using vision_recipes for fresh UOX fuel.

    Parameters
    ---------
    in_list: list
        list containing vision_recipes
    burnup: int
        burnup

    Returns
    -------
    data_dict: dict
        dictionary with key=[isotope],
        and value=[composition]
    """
    data_dict = {}
    for i in range(len(in_list)):
        if i > 1:
            if burnup == 33:
                data_dict.update({nn.id(in_list[i][0]):
                                  float(in_list[i][1])})
            elif burnup == 51:
                data_dict.update({nn.id(in_list[i][0]):
                                  float(in_list[i][3])})
            else:
                data_dict.update({nn.id(in_list[i][0]):
                                  float(in_list[i][5])})
    return data_dict


def get_composition_spent(in_list, burnup):
    """ Returns a dictionary of isotope and composition (in mass fraction)
    using vision_recipes for spent nuclear fuel

    Parameters
    ---------
    in_list: list
        list containing vision_recipes data
    burnup: int
        burnup

    Returns
    -------
    data_dict: dict
        dictionary with key=[isotope],
        and value=[composition]
    """
    data_dict = {}
    for i in range(len(in_list)):
        if i > 1:
            if burnup == 33:
                data_dict.update({nn.id(in_list[i][0]):
                                  float(in_list[i][2])})
            elif burnup == 51:
                data_dict.update({nn.id(in_list[i][0]):
                                  float(in_list[i][4])})
            else:
                data_dict.update({nn.id(in_list[i][0]):
                                  float(in_list[i][6])})
    return data_dict


def write_recipes(fresh_dict, spent_dict, in_template, burnup, region):
    """ Renders jinja template using fresh and spent fuel composition.

    Parameters
    ---------
    fresh_dict: dict
        dictionary with key=[isotope], and
        value=[composition] for fresh UOX
    spent_dict: dict
        dictionary with key=[isotope], and
        value=[composition] for spent fuel
    in_template: jinja template object
        jinja template object to be rendered
    burnup: int
        amount of burnup

    Returns
    -------
    null
        generates recipe files for cyclus.
    """
    out_path = 'cyclus/input/' + region + '/recipes/'
    pathlib.Path(out_path).mkdir(parents=True, exist_ok=True)
    rendered = in_template.render(fresh=fresh_dict,
                                  spent=spent_dict)
    with open(out_path + '/uox_' + str(burnup) + '.xml', 'w') as output:
        output.write(rendered)


def produce_recipes(in_csv, recipe_template, burnup):
    """ Generates commodity composition xml input for cyclus.

    Parameters
    ---------
    in_csv: str
        path and name of recipe file
    recipe_template: str
        path and name of recipe template
    burnup: int
        amount of burnup

    Returns
    -------
    null
        Generates commodity composition xml input for cyclus.
    """
    recipe = import_csv(in_csv, ',')
    write_recipes(get_composition_fresh(recipe, burnup),
                  get_composition_spent(recipe, burnup),
                  load_template(recipe_template), burnup)


def confirm_deployment(date_str, capacity):
    """ Confirms if reactor is to be deployed for CYCLUS by
    checking if the capacity > 400 and if the commercial date
    is a proper date format.

    Parameters
    ----------
    date_str: str
            the commercial date string from PRIS data file
    capacity: str
            capacity in MWe from RPIS data file

    Returns
    -------
    is_deployed: bool
            determines whether the reactor will be deployed
            in CYCLUS
    """
    is_deployed = False
    if len(date_str) > 4 and capacity > 400:
        try:
            date.parse(date_str)
        except:
            is_deployed = False
        is_deployed = True
    return is_deployed


def select_region(in_list, region):
    """ Returns a list of reactors that will be deployed for
    CYCLUS by checking the capacity and commercial date

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
    ASIA = {'IRAN', 'JAPAN', 'KAZAKHSTAN',
            'BANGLADESH', 'CHINA', 'INDIA',
            'UNITED ARAB EMIRATES', 'VIETNAM',
            'PAKISTAN', 'PHILIPPINES', 'SOUTH KOREA'
            }
    UNITED_STATES = {'UNITED STATES'}
    SOUTH_AMERICA = {'ARGENTINA', 'BRAZIL'}
    NORTH_AMERICA = {'CANADA', 'MEXICO', 'UNITED STATES'}
    EUROPE = {'UKRAINE', 'UNITED KINGDOM',
              'POLAND', 'ROMANIA', 'RUSSIA',
              'BELARUS', 'BELGIUM', 'BULGARIA',
              'GERMANY', 'ITALY', 'NETHERLANDS',
              'SWEDEN', 'SWITZERLAND', 'TURKEY',
              'SLOVENIA', 'SOVIET UNION', 'SPAIN',
              'CZECHOSLOVAKIA', 'FINLAND', 'FRANCE'
              }
    AFRICA = {'EGYPT', 'MOROCCO', 'SOUTH AFRICA', 'TUNISIA'}
    ALL = (SOUTH_AMERICA | NORTH_AMERICA |
           EUROPE | ASIA | AFRICA | UNITED_STATES)
    regions = {'ASIA': ASIA,
               'AFRICA': AFRICA,
               'EUROPE': EUROPE,
               'SOUTH_AMERICA': SOUTH_AMERICA,
               'NORTH_AMERICA': NORTH_AMERICA,
               'UNITED_STATES': UNITED_STATES,
               'ALL': ALL}
    if region.upper() not in regions.keys():
        raise ValueError(region + 'is not a valid region')
    reactor_list = []
    for row in in_list:
        country = row[0]
        if country.upper() in regions[region.upper()]:
            capacity = row[3]
            start_date = row[10]
            if confirm_deployment(start_date, capacity):
                reactor_list.append(row)
    return reactor_list


def get_lifetime(in_row):
    """ Calculates the lifetime of a reactor using first
    commercial date and shutdown date. Defaults to 720 months
    if shutdown date is not available.

    Parameters
    ----------
    in_row: list
        single row from PRIS data that contains reactor
        information

    Returns
    -------
    lifetime: int
        lifetime of reactor
    """
    comm_date = in_row[10]
    shutdown_date = in_row[11]
    if not shutdown_date.strip():
        return 720
    else:
        n_days_month = 365.0 / 12
        delta = (date.parse(shutdown_date) - date.parse(comm_date)).days
        return int(delta / n_days_month)


def write_reactors(in_list, out_path, reactor_template):
    """ Renders CYCAMORE::reactor specifications using jinja2.

    Parameters
    ----------
    in_list: list
        list containing PRIS data
    out_path: str
        output path for reactor files
    reactor_template: str
        path to reactor template

    Returns
    -------
    null
        writes xml files with CYCAMORE::reactor config
    """
    if out_path[-1] != '/':
        out_path += '/'
    pathlib.Path(out_path).mkdir(parents=True, exist_ok=True)
    reactor_template = load_template(reactor_template)
    for row in in_list:
        capacity = float(row[3])
        if capacity >= 400:
            name = row[1].replace(' ', '_')
            assem_per_batch = 0
            assem_no = 0
            assem_size = 0
            reactor_type = row[2]
            if reactor_type in ['BWR', 'ESBWR']:
                assem_no = 732
                assem_per_batch = int(assem_no / 3)
                assem_size = 138000 / assem_no
            elif reactor_type in ['GCR', 'HWGCR']:  # Need batch number
                assem_no = 324
                assem_per_batch = int(assem_no / 3)
                assem_size = 114000 / assem_no
            elif reactor_type == 'HTGR':  # Need batch number
                assem_no = 3944
                assem_per_batch = int(assem_no / 3)
                assem_size = 39000 / assem_no
            elif reactor_type == 'PHWR':
                assem_no = 390
                assem_per_batch = int(assem_no / 45)
                assem_size = 80000 / assem_no
            elif reactor_type == 'VVER':  # Need batch number
                assem_no = 312
                assem_per_batch = int(assem_no / 3)
                assem_size = 41500 / assem_no
            elif reactor_type == 'VVER-1200':  # Need batch number
                assem_no = 163
                assem_per_batch = int(assem_no / 3)
                assem_size = 80000 / assem_no
            else:
                assem_no = 241
                assem_per_batch = int(assem_no / 3)
                assem_size = 103000 / assem_no
            config = reactor_template.render(name=name,
                                             lifetime=get_lifetime(row),
                                             assem_size=assem_size,
                                             n_assem_core=assem_no,
                                             n_assem_batch=assem_per_batch,
                                             power_cap=row[3],
                                             lon=row[14],
                                             lat=row[13])
            with open(out_path + name.replace(' ', '_') + '.xml',
                      'w') as output:
                output.write(config)


def obtain_reactors(in_csv, region, reactor_template):
    """ Writes xml files for individual reactors in a given
    region.

    Parameters
    ----------
    in_csv: str
        csv file name
    region: str
        region name
    reactor_template: str
        path to CYCAMORE::reactor config template file

    Returns
    -------
    null
        Writes xml files for individual reactors in region.
    """
    in_data = import_csv(in_csv, ',')
    reactor_list = select_region(in_data, region)
    out_path = 'cyclus/input/' + region + '/reactors'
    write_reactors(reactor_list, out_path, reactor_template)


def write_deployment(in_dict, out_path, deployinst_template,
                     inclusions_template):
    """ Renders jinja template using dictionary of reactor name and buildtime.
    Outputs an xml file that uses xinclude to include the reactor xml files
    located in cyclus_input/reactors.

    Parameters
    ---------
    in_dict: dictionary
        dictionary with key=[reactor name], and value=[buildtime]
    out_path: str
        output path for files
    deployinst_template: str
        path to deployinst template
    inclusions_template: str
        path to inclusions template

    Returns
    -------
    null
        generates input files that have deployment and xml inclusions
    """
    if out_path[-1] != '/':
        out_path += '/'
    pathlib.Path(out_path).mkdir(parents=True, exist_ok=True)
    deployinst_template = load_template(deployinst_template)
    inclusions_template = load_template(inclusions_template)
    country_list = {value[0] for value in in_dict.values()}
    for nation in country_list:
        temp_dict = {}
        for reactor in in_dict.keys():
            if in_dict[reactor][0].upper() == nation.upper():
                temp_dict.update({reactor: in_dict[reactor][1]})
        pathlib.Path(out_path + nation.replace(' ', '_') +
                     '/').mkdir(parents=True, exist_ok=True)
        deployinst = deployinst_template.render(reactors=temp_dict)
        with open(out_path + nation.replace(' ', '_') +
                  '/deployinst.xml', 'w') as output1:
            output1.write(deployinst)
    inclusions = inclusions_template.render(reactors=in_dict)
    with open(out_path + 'inclusions.xml', 'w') as output2:
        output2.write(inclusions)


def get_buildtime(in_list, start_year, path_list):
    """ Calculates the buildtime required for reactor
    deployment in months.

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
    buildtime_dict: dict
        dictionary with key=[name of reactor], and
        value=[set of country and buildtime]
    """
    buildtime_dict = {}
    for row in in_list:
        comm_date = date.parse(row[10])
        start_date = [comm_date.year, comm_date.month, comm_date.day]
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


def deploy_reactors(in_csv, region, start_year, deployinst_template,
                    inclusions_template, reactors_path, deployment_path):
    """ Generates xml files that specify the reactors that will be included
    in a CYCLUS simulation.

    Parameters
    ---------
    in_csv: str
        path to pris reactor database
    region: str
        region name
    start_year: int
        starting year of simulation
    deployinst_template: str
        path to deployinst template
    inclusions_template: str
        path to inclusions template
    reactors_path: str
        path containing reactor files
    deployment_path: str
        output path for deployinst xml

    Returns
    -------
    buildtime_dict: dict
        dictionary with key=[name of reactor], and
        value=[set of country and buildtime]
    """
    lists = []
    if reactors_path[-1] != '/':
        reactors_path += '/'
    for files in os.listdir(reactors_path):
        lists.append(reactors_path + files)
    in_data = import_csv(in_csv, ',')
    reactor_list = select_region(in_data, region)
    buildtime = get_buildtime(reactor_list, start_year, lists)
    write_deployment(buildtime, deployment_path, deployinst_template,
                     inclusions_template)
    return buildtime


def render_cyclus(cyclus_template, region, in_dict, out_path):
    """ Renders final CYCLUS input file with xml base, and institutions
    for each country

    Parameters
    ----------
    cyclus_template: str
        path to CYCLUS input file template
    region: str
        region chosen for CYCLUS simulation
    in_dict: dictionary
        in_dict should be buildtime_dict from get_buildtime function
    out_path: str
        output path for CYCLUS input file
    output_name:

    Returns
    -------
    null
        writes CYCLUS input file in out_path
    """
    if out_path[-1] != '/':
        out_path += '/'
    cyclus_template = load_template(cyclus_template)
    country_list = {value[0].replace(' ', '_') for value in in_dict.values()}
    rendered = cyclus_template.render(countries=country_list,
                                      base_dir=os.path.abspath(out_path) + '/')
    with open(out_path + region + '.xml', 'w') as output:
        output.write(rendered)
