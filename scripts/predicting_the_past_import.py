import csv
import dateutil.parser as date
import jinja2
import numpy as np
import os
import pathlib
import pandas as pd
import sqlite3 as sql
from fuzzywuzzy import fuzz
from pyne import nucname as nn


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


def import_pris(pris_link):
    """ Opens pris_csv using Pandas. Adds Latitude and Longitude
    columns

    Parameters
    ----------
    pris_link: str
        path to reactors_pris_2016.original.csv file

    Returns
    -------
    pris: pd.Dataframe
        pris database
    """
    pris = pd.read_csv(pris_link,
                       delimiter=',',
                       encoding='iso-8859-1',
                       skiprows=20,
                       )

    pris = pris.rename(columns={pris.columns[2]: 'Country'})
    pris = pris[['Country', 'Unit', 'Current Status', 'Type',
                 'Model', 'Operator', 'Reactor Supplier', 'Const. Date',
                 'Grid Date', 'Shutdown Date', 'RUP [MWe]']]
    pris.insert(11, 'Latitude', np.nan)
    pris.insert(12, 'Longitude', np.nan)
    pris = pris[pris.Unit.notnull()]
    pris = pris[pris.Unit != 'Unit']
    pris = pris.replace(np.nan, '')
    return pris


def import_webscrape_data(scrape_link):
    """ Returns sqlite content of webscrape by performing an
    sqlite query

    Parameters
    ----------
    scrape_link: str
        path to webscrape.sqlite file

    Returns
    -------
    coords: sqlite cursor
        sqlite cursor containing webscrape data
    """
    cur = get_cursor(scrape_link)
    coords = cur.execute("SELECT name, long, lat FROM reactors_coordinates")
    return coords


def get_edge_cases():
    """ Returns a dictionary of edge cases that fuzzywuzzy is
    unable to catch. This could be because PRIS database stores
    reactor names and Webscrape database fetches power plant names,
    or because PRIS reactor names are abbreviated.

    Parameters
    ----------

    Returns
    -------
    others: dict
        dictionary of edge cases with "key=pris_reactor_name, and
        value=webscrape_plant_name"
    """
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
              'ZAPOROZHYE-': 'Zaporizhzhya',
              'ROBINSON-': 'H. B. Robinson',
              'SUMMER-': 'Virgil C. Summer',
              'FARLEY-': 'Joseph M. Farley',
              'ST. LAURENT ': 'Saint-Laurent',
              'HADDAM NECK': 'Connecticut1 Yankee',
              'FITZPATRICK': 'James A. FitzPatrick',
              'HIGASHI DORI-1 (TOHOKU)': 'Higashidōri',
              }
    return others


def sanitize_webscrape_name(name):
    """ Sanitizes webscrape powerplant names by removing unwanted
    strings (listed in blacklist), applying lower case, and deleting
    trailing whitespace.

    Parameters
    ----------
    name: str
        webscrape plant name

    Returns
    -------
    name: str
        sanitized name for use with fuzzywuzzy
    """
    blacklist = ['nuclear', 'power',
                 'plant', 'generating',
                 'station', 'reactor', 'atomic',
                 'energy', 'center', 'electric']
    name = name.lower()
    for blacklisted in blacklist:
        name = name.replace(blacklisted, '')
    name = name.strip()
    name = ' '.join(name.split())
    return name


def sanitize_pris_name(name):
    pris_name = name.lower()
    if pris_name.find('-') != -1 and is_int(pris_name[-1]):
        if pris_name[pris_name.find('-') + 1:].find('-') != -1:
            idx = pris_name.find('-')
            idx += pris_name[pris_name.find('-') + 1:].find('-')
            pris_name = pris_name[:idx]
        else:
            pris_name = pris_name[:pris_name.find('-')]
    return pris_name


def is_int(str):
    """ Checks if input string is a number rather than a letter

    Parameters
    ----------
    str: str
        string to test

    Returns
    -------
    answer: bool
        returns True if string is a number; False if string is not
    """
    answer = False
    try:
        int(str)
    except ValueError:
        return answer
    answer = True
    return answer


def merge_coordinates(pris_link, scrape_link, data_year):
    """ Obtains coordinates from webscrape.sqlite and
    writes them to matching reactors in PRIS reactor file.

    Parameters
    ----------
    pris_link: str
        path and name of pris reactor text file
    scrape: str
        path and name of webscrape sqlite file
    data_year: int
        year the data is pulled from

    Returns
    -------
    null
        Writes pris text file with coordinates
    """
    others = get_edge_cases()
    pris = import_pris(pris_link)
    coords = import_webscrape_data(scrape_link)
    for web in coords:
        for i, prs in pris.iterrows():
            webscrape_name = sanitize_webscrape_name(web['name'])
            pris_name = sanitize_pris_name(prs[1])
            if fuzz.ratio(webscrape_name, pris_name) > 78:
                prs['Latitude'] = web['lat']
                prs['Longitude'] = web['long']
            else:
                for other in others.keys():
                    edge_case_key = other.lower()
                    edge_case_value = others[other].lower()
                    if fuzz.ratio(pris_name, edge_case_key) > 80:
                        if fuzz.ratio(webscrape_name, edge_case_value) > 75:
                            prs['Latitude'] = web['lat']
                            prs['Longitude'] = web['long']
    pris.to_csv(
        '../database/reactors_pris_' +
        str(data_year) +
        '.csv',
        index=False,
        sep=',')


def save_output(pris, data_year):
    """ Saves updated PRIS database as 'reactors_pris_2016.csv'

    Parameters
    ----------
    pris: pd.DataFrame
        updated PRIS database with latitude and longitude info
    data_year: int
        year the data is pulled from

    Returns
    -------

    """
    pris.to_csv('../database/reactors_pris_' + str(data_year) + '.csv',
                index=False,
                sep=',',
                )


def import_csv(in_csv, delimit=','):
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


def write_recipes(fresh_dict, spent_dict, in_template,
                  burnup, out_path):
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
    out_path: str
        output path for recipe files

    Returns
    -------
    null
        generates recipe files for cyclus.
    """
    pathlib.Path(out_path).mkdir(parents=True, exist_ok=True)
    rendered = in_template.render(fresh=fresh_dict,
                                  spent=spent_dict)
    with open(out_path + '/uox_' + str(burnup) + '.xml', 'w') as output:
        output.write(rendered)


def produce_recipes(in_csv, recipe_template, burnup, out_path):
    """ Generates commodity composition xml input for cyclus.

    Parameters
    ---------
    in_csv: str
        path and name of recipe file
    recipe_template: str
        path and name of recipe template
    burnup: int
        amount of burnup
    out_path: str
        output path for recipe files

    Returns
    -------
    null
        Generates commodity composition xml input for cyclus.
    """
    recipe = import_csv(in_csv, ',')
    write_recipes(get_composition_fresh(recipe, burnup),
                  get_composition_spent(recipe, burnup),
                  load_template(recipe_template), burnup, out_file)


def confirm_deployment(row, start_year):
    """ Confirms if reactor is to be deployed for CYCLUS by
    checking if the capacity > 400 and if the commercial date
    is a proper date format.

    Parameters
    ----------
    date_str: str
        the commercial date string from PRIS data file
    capacity: str
        capacity in MWe from PRIS data file
    start_year: int
        start year of the simulation
    Returns
    -------
    is_deployed: bool
            determines whether the reactor will be deployed
            in CYCLUS
    """
    is_deployed = False
    capacity = row['RUP [MWe]']
    start_date = str(row['Grid Date'])
    end_date = str(row['Shutdown Date'])
    if len(start_date) > 4 and float(capacity) > 400:
        if end_date == 'nan':
            try:
                date.parse(start_date)
                is_deployed = True
            except BaseException:
                pass
        elif date.parse(end_date).year > start_year:
            try:
                date.parse(start_date)
                is_deployed = True
            except BaseException:
                pass
    return is_deployed


def select_region(in_dataframe, region, start_year):
    """ Returns a list of reactors that will be deployed for
    CYCLUS by checking the capacity and commercial date

    Parameters
    ----------
    in_dataframe: DataFrame
        imported csv file in DataFrame format
    region: str
        name of the region
    start_year: int
        start year of simulation

    Returns
    -------
    reactor_df: DataFrame
            DataFrame of reactors from PRIS
    """
    ASIA = {'IRAN, ISLAMIC REPUBLIC OF', 'JAPAN',
            'KAZAKHSTAN',
            'BANGLADESH', 'CHINA', 'INDIA',
            'UNITED ARAB EMIRATES', 'VIETNAM',
            'PAKISTAN', 'PHILIPPINES', 'KOREA, REPUBLIC OF',
            'KAZAKHSTAN', 'ARMENIA', 'TAIWAN, CHINA'
            }
    UNITED_STATES = {'UNITED STATES OF AMERICA'}
    SOUTH_AMERICA = {'ARGENTINA', 'BRAZIL'}
    NORTH_AMERICA = {'CANADA', 'MEXICO', 'UNITED STATES OF AMERICA'}
    EUROPE = {'UKRAINE', 'UNITED KINGDOM',
              'POLAND', 'ROMANIA', 'RUSSIA',
              'BELARUS', 'BELGIUM', 'BULGARIA',
              'GERMANY', 'ITALY', 'NETHERLANDS',
              'SWEDEN', 'SWITZERLAND', 'TURKEY',
              'SLOVENIA', 'SOVIET UNION', 'SPAIN',
              'CZECH REPUBLIC', 'FINLAND', 'FRANCE',
              'SLOVAKIA', 'HUNGARY', 'LITHUANIA'
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
    reactor_df = pd.DataFrame(columns=in_dataframe.columns)
    for index, row in in_dataframe.iterrows():
        country = row['Country']
        if country.upper() in regions[region.upper()]:
            if confirm_deployment(row, start_year):
                reactor_df = reactor_df.append(
                    in_dataframe.loc[index], ignore_index=True)
    reactor_df = reactor_df.replace(np.nan, '')
    reactor_df = reactor_df.astype(str)

    return reactor_df


def get_lifetime(in_row, start_year):
    """ Calculates the lifetime of a reactor using first
    commercial date and shutdown date. Defaults to 720 months
    if shutdown date is not available.

    Parameters
    ----------
    in_row: list
        single row from PRIS data that contains reactor
        information
    start_year: int
        start year for the simulation

    Returns
    -------
    lifetime: int
        lifetime of reactor
    """
    comm_date = in_row['Grid Date']
    if date.parse(comm_date).year < start_year:
        comm_date = str(start_year) + '-02-01'
    shutdown_date = in_row['Shutdown Date']
    if not shutdown_date.strip():
        return 720
    else:
        n_days_month = 365.0 / 12
        delta = (date.parse(shutdown_date) - date.parse(comm_date)).days
        return int(delta / n_days_month)


def write_reactors(in_dataframe, out_path, reactor_template, start_year,
                   cycle_time=18, refuel_time=1):
    """ Renders CYCAMORE::reactor specifications using jinja2.

    Parameters
    ----------
    in_dataframe: DataFrame
        DataFrame containing PRIS data
    out_path: str
        output path for reactor files
    reactor_template: str
        path to reactor template
    start_year: int
        start year of the simulation
    cycle_time: int
        cycle length of reactors in months
    refuel_time: int
        average refuel time in months

    Returns
    -------
    null
        writes xml files with CYCAMORE::reactor config
    """
    if out_path[-1] != '/':
        out_path += '/'
    pathlib.Path(out_path).mkdir(parents=True, exist_ok=True)
    reactor_template = load_template(reactor_template)
    for index, row in in_dataframe.iterrows():
        capacity = float(row['RUP [MWe]'])
        if capacity >= 400:
            name = row[1].replace(' ', '_')
            assem_per_batch = 0
            assem_no = 0
            assem_size = 0
            reactor_type = row['Type']
            latitude = row['Latitude'] if row['Latitude'] != '' else 0
            longitude = row['Longitude'] if row['Longitude'] != '' else 0
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
                                             lifetime=get_lifetime(
                                                 row, start_year),
                                             cycletime=cycle_time,
                                             refueltime=refuel_time,
                                             assem_size=assem_size,
                                             n_assem_core=assem_no,
                                             n_assem_batch=assem_per_batch,
                                             power_cap=row['RUP [MWe]'],
                                             lon=longitude,
                                             lat=latitude)
            with open(out_path + name.replace(' ', '_') + '.xml',
                      'w') as output:
                output.write(config)


def obtain_reactors(in_csv, region, reactor_template, out_path, start_year):
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
    out_path: str
        output path for reactor files
    start_year: int
        start year of the simulation

    Returns
    -------
    null
        Writes xml files for individual reactors in region.
    """
    in_data = pd.read_csv(in_csv, ',')
    reactor_list = select_region(in_data, region, start_year)
    write_reactors(reactor_list, out_path, reactor_template, start_year)


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
    for index, row in in_list.iterrows():
        comm_date = date.parse(row['Grid Date'])
        start_date = [comm_date.year, comm_date.month, comm_date.day]
        delta = ((start_date[0] - int(start_year)) * 12 +
                 (start_date[1]) +
                 round(start_date[2] / (365.0 / 12)))
        if delta < 0:
            delta = 1
        for index, reactor in enumerate(path_list):
            name = row['Unit'].replace(' ', '_')
            country = row['Country']
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
    in_data = pd.read_csv(in_csv)
    reactor_list = select_region(in_data, region, start_year)
    buildtime = get_buildtime(reactor_list, start_year, lists)
    write_deployment(buildtime, deployment_path, deployinst_template,
                     inclusions_template)
    return buildtime


def render_cyclus(cyclus_template, region, in_dict,
                  out_path, start_year, duration=780, burn_up=50):
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
    start_year: int
        start year for the simulation
    duration: int
        duration for CYCLUS simulation to last in months
    burn_up: int
        burnup in GWd/MTU

    Returns
    -------
    null
        writes CYCLUS input file in out_path
    """
    if out_path[-1] != '/':
        out_path += '/'
    cyclus_template = load_template(cyclus_template)
    country_list = {value[0].replace(' ', '_') for value in in_dict.values()}
    rendered = cyclus_template.render(start_year=start_year,
                                      duration=duration, 
                                      burnup=burn_up,
                                      countries=country_list,
                                      base_dir=os.path.abspath(out_path) + '/')
    with open(out_path + region + '.xml', 'w') as output:
        output.write(rendered)
