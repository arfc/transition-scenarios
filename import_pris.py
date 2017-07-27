import import_data as indata


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
    in_template: str
            name of reactor template file

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
        elif reactor_type == 'PWR':
            assem_no = 240
            assem_per_batch = assem_no / 3
            assem_size = 417
        elif reactor_type == 'PHWR':
            assem_no = 347
            assem_per_batch = assem_no /
        elif reactor_type == 'WCR':
        elif reactor_type == 'GCR':
        elif reactor_type == 'FBR':
        elif reactor_type == 'LWGR':
