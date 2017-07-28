import import_data as indata
import numpy as np
import write_deployinst_input as wdi


def select_region(in_list, region):
    """ Returns a list of reactors by region

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
    regions = {'SOUTH_AMERICA': SOUTH_AMERICA, 'NORTH_AMERICA': NORTH_AMERICA,
               'ASIA': ASIA, 'AFRICA': AFRICA, 'EUROPE': EUROPE}

    if region.upper() not in regions.keys():
        raise ValueError(region + 'is not a valid region')
    reactor_list = []
    for row in in_list:
        country = in_list[row][0]
        if country in regions[region]:
            reactor_list.append(in_list[row])
    return reactor_list


def write_reactors(in_list, in_template):
    """ Obtains information regarding reactors
    and renders the information into a jinja template

    Parameters
    ----------
    in_list: list
            list containing PRIS data
    in_template: jinja template object
            jinja template object to be rendered.

    Returns
    -------
    null
    """
    reactor_template = indata.load_template(in_template)
    for row in in_list:
        capacity = float(in_list[row][3])
        if capacity >= 400:
            name = in_list[row][0]
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
        rendered = in_template.render(name=name,
                                      lifetime=get_lifetime(name),
                                      assem_size=assem_size,
                                      n_assem_core=assem_no,
                                      n_assem_batch=assem_per_batch,
                                      power_cap=in_list[row][3])
        with open('cyclus/input/europe_test/reactors/' +
                  name.replace(' ', '_') +
                  '.xml', 'w') as output:
            output.write(rendered)


def get_lifetime(in_list):
