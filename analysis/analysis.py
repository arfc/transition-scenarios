import collections
import csv
import numpy as np
import matplotlib.pyplot as plt
import sqlite3 as lite
import sys
from matplotlib import cm
from pyne import nucname


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
    con = lite.connect(file_name)
    con.row_factory = lite.Row
    return con.cursor()


def get_agent_ids(cur, archetype):
    """ Gets all agentIds from Agententry table for wanted archetype

        agententry table has the following format:
            SimId / AgentId / Kind / Spec /
            Prototype / ParentID / Lifetime / EnterTime

    Parameters
    ----------
    cur: cursor
        sqlite cursor3
    archetype: str
        agent's archetype specification

    Returns
    -------
    id_list: list
        list of all agentId strings
    """
    agents = cur.execute("SELECT agentid FROM agententry WHERE spec "
                         "LIKE '%" + archetype + "%' COLLATE NOCASE"
                         ).fetchall()

    return list(str(agent['agentid']) for agent in agents)


def get_prototype_id(cur, prototype):
    """ Returns agentid of a prototype

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    prototype: str
        name of prototype

    Returns
    -------
    agent_id: list
        list of prototype agent_ids as strings
    """
    ids = cur.execute('SELECT agentid FROM agententry '
                      'WHERE prototype = "' +
                      str(prototype) + '" COLLATE NOCASE').fetchall()

    return list(str(agent['agentid']) for agent in ids)


def get_inst(cur):
    """ Returns prototype and agentids of institutions

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor

    Returns
    -------
    sqlite query result (list of tuples)
    """
    return cur.execute('SELECT prototype, agentid FROM agententry '
                       'WHERE kind = "Inst"').fetchall()


def timestep_to_years(init_year, timestep):
    """ Returns list of years in simulation

    Parameters
    ----------
    init_year: int
        initial year in simulation
    timestep: np.array
        timestep of simulation (months)

    Returns
    -------
    array of years
    """

    return init_year + (timestep / 12)


def exec_string(in_list, search, request_colmn):
    """ Generates sqlite query command to select things and
        inner join resources and transactions.

    Parameters
    ----------
    in_list: list
        list of items to specify search
        This variable will be inserted as sqlite
        query arugment following the search keyword
    search: str
        criteria for in_list search
        This variable will be inserted as sqlite
        query arugment following the WHERE keyword
    request_colmn: str
        column (set of values) that the sqlite query should return
        This variable will be inserted as sqlite
        query arugment following the SELECT keyword

    Returns
    -------
    str
        sqlite query command.
    """
    if len(in_list) == 0:
        raise Exception('Cannot create an exec_string with an empty list')
    if type(in_list[0]) == str:
        in_list = ['"' + x + '"' for x in in_list]

    query = ("SELECT " + request_colmn +
             " FROM resources INNER JOIN transactions"
             " ON transactions.resourceid = resources.resourceid"
             " WHERE (" + str(search) + ' = ' + str(in_list[0])
             )
    for item in in_list[1:]:
        query += ' OR ' + str(search) + ' = ' + str(item)
    query += ')'

    return query


def get_timesteps(cur):
    """ Returns simulation start year, month, duration and
    timesteps (in numpy linspace).

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor

    Returns
    -------
    init_year: int
        start year of simulation
    init_month: int
        start month of simulation
    duration: int
        duration of simulation
    timestep: list
        linspace up to duration
    """
    info = cur.execute('SELECT initialyear, initialmonth, '
                       'duration FROM info').fetchone()
    init_year = info['initialyear']
    init_month = info['initialmonth']
    duration = info['duration']
    timestep = np.linspace(0, duration - 1, num=duration)

    return init_year, init_month, duration, timestep


def get_timeseries(in_list, duration, kg_to_tons):
    """ returns a timeseries list from in_list data.

    Parameters
    ----------
    in_list: list
        list of data to be created into timeseries
        list[0] = time
        list[1] = value, quantity
    duration: int
        duration of the simulation
    kg_to_tons: bool
        if True, list returned has units of tons
        if False, list returned as units of kilograms

    Returns
    -------
    timeseries list of commodities stored in in_list
    """
    value = 0
    value_timeseries = []
    array = np.array(in_list)
    if len(in_list) > 0:
        for i in range(0, duration):
            value = sum(array[array[:, 0] == i][:, 1])
            if kg_to_tons:
                value_timeseries.append(value * 0.001)
            else:
                value_timeseries.append(value)
    return value_timeseries


def get_timeseries_cum(in_list, duration, kg_to_tons):
    """ returns a timeseries list from in_list data.

    Parameters
    ----------
    in_list: list
        list of data to be created into timeseries
        list[0] = time
        list[1] = value, quantity
    multiplyby: int
        integer to multiply the value in the list by for
        unit conversion from kilograms
    kg_to_tons: bool
        if True, list returned has units of tons
        if False, list returned as units of kilograms

    Returns
    -------
    timeseries of commodities in kg or tons
    """
    value = 0
    value_timeseries = []
    array = np.array(in_list)
    if len(in_list) > 0:
        for i in range(0, duration):
            value += sum(array[array[:, 0] == i][:, 1])
            if kg_to_tons:
                value_timeseries.append(value * 0.001)
            else:
                value_timeseries.append(value)
    return value_timeseries


def get_isotope_transactions(resources, compositions):
    """Creates a dictionary with isotope name, mass, and time

    Parameters
    ----------
    resources: list of tuples
        resource data from the resources table
        (times, sum(quantity), qualid)
    compositions: list of tuples
        composition data from the compositions table
        (qualid, nucid, massfrac)

    Returns
    -------
    transactions: dictionary
        dictionary with "key=isotope, and
        value=list of tuples (time, mass_moved)"
    """
    transactions = collections.defaultdict(list)
    for res in resources:
        for comp in compositions:
            if res['qualid'] == comp['qualid']:
                transactions[comp['nucid']].append((res['time'],
                                                    res['sum(quantity)'] *
                                                    comp['massfrac']))

    return transactions


def facility_commodity_flux(cur, agent_ids, commod_list, is_outflux):
    """ Returns timeseries of commodity in/outflux from agents

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    agent_ids: list
        list of agentids
    commod_list: list
        list of commodities
    is_outflux: bool
        gets outflux if True, influx if False

    Returns
    -------
    commodity_dict: dictionary
        dictionary with "key=commodity, and
        value=timeseries list of masses in kg"
    """
    init_year, init_month, duration, timestep = get_timesteps(cur)
    commodity_dict = collections.OrderedDict()
    for comm in commod_list:
        query = (exec_string(agent_ids, 'receiverid',
                             'time, sum(quantity), qualid') +
                 ' and (commodity = "' + str(comm) +
                 '") GROUP BY time')
        # outflux changes receiverid to senderid
        if is_outflux:
            query = query.replace('receiverid', 'senderid')

        res = cur.execute(query).fetchall()

        timeseries = get_timeseries_cum(res, duration, True)
        commodity_dict[comm] = timeseries

    return commodity_dict


def facility_commodity_flux_isotopics(cur, agent_ids,
                                      commod_list, is_outflux):
    """ Returns timeseries isotoptics of commodity in/outflux
    from agents

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    agent_ids: list
        list of agentids
    commod_list: list
        list of commodities
    is_outflux: bool
        gets outflux if True, influx if False

    Returns
    -------
    iso_dict: dictionary
        dictionary with "key=isotope, and
        value=timeseries list of masses in kg"
    """
    init_year, init_month, duration, timestep = get_timesteps(cur)
    iso_dict = collections.defaultdict(list)
    for comm in commod_list:
        query = ('SELECT time, sum(quantity)*massfrac, nucid '
                 'FROM transactions INNER JOIN resources '
                 'ON resources.resourceid = transactions.resourceid '
                 'LEFT OUTER JOIN compositions '
                 'ON compositions.qualid = resources.qualid '
                 'WHERE (receiverid = ' +
                 ' OR receiverid = '.join(agent_ids) +
                 ') AND (commodity = "' + str(comm) +
                 '") GROUP BY time, nucid')
        # outflux changes receiverid to senderid
        if is_outflux:
            query = query.replace('receiverid', 'senderid')

        res = cur.execute(query).fetchall()
        for time, amount, nucid in res:
            iso_dict[nucname.name(nucid)].append((time, amount))
    for key in iso_dict:
        iso_dict[key] = get_timeseries_cum(iso_dict[key], duration, True)

    return iso_dict


def get_stockpile(cur, facility):
    """ gets inventory timeseries in a fuel facility

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    facility: str
        name of facility

    Returns
    -------
    pile_dict: dictionary
        dictionary with "key=agent type, and
        value=timeseries list of stockpile"
    """
    pile_dict = collections.OrderedDict()
    agentid = get_agent_ids(cur, facility)
    query = exec_string(agentid, 'agentid', 'timecreated, quantity, qualid')
    query = query.replace('transactions', 'agentstateinventories')
    stockpile = cur.execute(query).fetchall()
    init_year, init_month, duration, timestep = get_timesteps(cur)
    stock_timeseries = get_timeseries_cum(stockpile, duration, True)
    pile_dict[facility] = stock_timeseries

    return pile_dict


def get_swu_dict(cur):
    """ returns dictionary of swu timeseries for each enrichment plant

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor

    Returns
    -------
    swu_dict: dictionary
        dictionary with "key=Enrichment (facility number), and
        value=swu timeseries list"
    """
    swu_dict = collections.OrderedDict()
    agentid = get_agent_ids(cur, 'Enrichment')
    init_year, init_month, duration, timestep = get_timesteps(cur)
    for num in agentid:
        swu_data = cur.execute('SELECT time, value '
                               'FROM timeseriesenrichmentswu '
                               'WHERE agentid = ' + str(num)).fetchall()
        swu_timeseries = get_timeseries_cum(swu_data, duration, False)
        swu_dict['Enrichment_' + str(num)] = swu_timeseries

    return swu_dict


def get_power_dict(cur):
    """ Gets dictionary of power capacity by calling capacity_calc

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor

    Returns
    ------
    power_dict: dictionary
        "dictionary with key=government, and
        value=timeseries list of installed capacity"
    """
    init_year, init_month, duration, timestep = get_timesteps(cur)
    governments = get_inst(cur)

    # get power cap values
    entry = cur.execute('SELECT max(value), timeseriespower.agentid, '
                        'parentid, entertime FROM agententry '
                        'INNER JOIN timeseriespower '
                        'ON agententry.agentid = timeseriespower.agentid '
                        'GROUP BY timeseriespower.agentid').fetchall()

    exit_step = cur.execute('SELECT max(value), timeseriespower.agentid, '
                            'parentid, exittime FROM agentexit '
                            'INNER JOIN timeseriespower '
                            'ON agentexit.agentid = timeseriespower.agentid'
                            ' INNER JOIN agententry '
                            'ON agentexit.agentid = agententry.agentid '
                            'GROUP BY timeseriespower.agentid').fetchall()

    return capacity_calc(governments, timestep, entry, exit_step)


def get_deployment_dict(cur):
    """ Gets dictionary of reactors deployed over time
    by calling reactor_deployments

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor

    Returns
    ------
    num_dict: dictionary
        "dictionary with key=government, and
        value=timeseries list of number of reactors"
    """
    init_year, init_month, duration, timestep = get_timesteps(cur)
    governments = get_inst(cur)

    # get power cap values
    entry = cur.execute('SELECT max(value), timeseriespower.agentid, '
                        'parentid, entertime FROM agententry '
                        'INNER JOIN timeseriespower '
                        'ON agententry.agentid = timeseriespower.agentid '
                        'GROUP BY timeseriespower.agentid').fetchall()

    exit_step = cur.execute('SELECT max(value), timeseriespower.agentid, '
                            'parentid, exittime FROM agentexit '
                            'INNER JOIN timeseriespower '
                            'ON agentexit.agentid = timeseriespower.agentid'
                            ' INNER JOIN agententry '
                            'ON agentexit.agentid = agententry.agentid '
                            'GROUP BY timeseriespower.agentid').fetchall()
    return reactor_deployments(governments, timestep, entry, exit_step)


def fuel_usage_timeseries(cur, fuel_list):
    """ Calculates total fuel usage over time

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    fuel_list: list
        list of fuel commodity names (eg. uox, mox) as string
        to consider in fuel usage.

    Returns
    -------
    fuel_dict: dictionary
        dictionary with "key=fuel (from fuel_list),
        value=timeseries list of fuel amount [kg]"
    """
    fuel_dict = collections.OrderedDict()
    init_year, init_month, duration, timestep = get_timesteps(cur)
    for fuel in fuel_list:
        temp_list = [fuel]
        fuel_quantity = cur.execute(exec_string(temp_list, 'commodity',
                                                'time, sum(quantity)') +
                                    ' GROUP BY time').fetchall()
        quantity_timeseries = []
        try:
            quantity_timeseries = get_timeseries_cum(
                fuel_quantity, duration, True)
            fuel_dict[fuel] = quantity_timeseries
        except:
            print(str(fuel) + ' has not been used.')

    return fuel_dict


def nat_u_timeseries(cur):
    """ Finds natural uranium supply from source
        Since currently the source supplies all its capacity,
        the timeseriesenrichmentfeed is used.

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor

    Returns
    -------
    get_timeseries: function
        calls a function that returns timeseries list of natural U
        demand from enrichment [MTHM]
    """
    init_year, init_month, duration, timestep = get_timesteps(cur)

    # Get Nat U feed to enrichment from timeseriesenrichmentfeed
    feed = cur.execute('SELECT time, sum(value) '
                       'FROM timeseriesenrichmentfeed '
                       'GROUP BY time').fetchall()
    return get_timeseries_cum(feed, duration, True)


def get_trade_dict(cur, sender, receiver, is_prototype, do_isotopic):
    """ Returns trade timeseries between two prototypes' or facilities
    with or without isotopics

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    sender: str
        name of sender as facility type or prototype name
    receiver: str
        name of receiver as facility type or prototype name
    is_prototype: bool
        if True, search sender and receiver as prototype,
        if False, as facility type from spec.
    do_isotopic: bool
        if True, perform isotopics (takes significantly longer)

    Returns:
    --------
    return_dict: dictionary
        if do_isotopic:
            dictionary with "key=isotope, and
                        value=timeseries list
                        of mass traded between
                        two prototypes"
        else:
            dictionary with "key=string, sender to receiver,
                        value=timeseries list of mass traded
                        between two prototypes"

    """
    init_year, init_month, duration, timestep = get_timesteps(cur)
    iso_dict = collections.defaultdict(list)
    return_dict = collections.defaultdict()

    if is_prototype:
        sender_id = get_prototype_id(cur, sender)
        receiver_id = get_prototype_id(cur, receiver)
    else:
        sender_id = get_agent_ids(cur, sender)
        receiver_id = get_agent_ids(cur, receiver)

    if do_isotopic:
        trade = cur.execute('SELECT time, sum(quantity)*massfrac, nucid '
                            'FROM transactions INNER JOIN resources ON '
                            'resources.resourceid = transactions.resourceid '
                            'LEFT OUTER JOIN compositions '
                            'ON compositions.qualid = resources.qualid '
                            'WHERE (senderid = ' +
                            'OR senderid = '.join(sender_id) +
                            ') AND (receiverid = ' +
                            ' OR receiverid = '.join(receiver_id) +
                            ') GROUP BY time, nucid').fetchall()
    else:
        trade = cur.execute('SELECT time, sum(quantity), qualid '
                            'FROM transactions INNER JOIN resources ON '
                            'resources.resourceid = transactions.resourceid'
                            ' WHERE (senderid = ' +
                            ' OR senderid = '.join(sender_id) +
                            ') AND (receiverid = ' +
                            ' OR receiverid = '.join(receiver_id) +
                            ') GROUP BY time').fetchall()

    if do_isotopic:
        for time, amount, nucid in trade:
            iso_dict[nucname.name(nucid)].append((time, amount))
        for key in iso_dict:
            iso_dict[key] = get_timeseries_cum(iso_dict[key], True)
        return iso_dict
    else:
        key_name = str(sender)[:5] + ' to ' + str(receiver)[:5]
        return_dict[key_name] = get_timeseries_cum(trade, True)
        return return_dict


def final_stockpile(cur, facility):
    """ get final stockpile in a fuel facility

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    facility: str
        name of facility

    Returns
    -------
    outstring: str
        MTHM value of stockpile
    """
    agentid = get_agent_ids(cur, facility)
    outstring = ''
    for agent in agentid:
        count = 1
        name = cur.execute('SELECT prototype FROM agententry'
                           'WHERE agentid = ' + str(agent)).fetchone()

        outstring += 'The Stockpile in ' + str(name[0]) + ' : \n \n'
        stkpile = cur.execute('SELECT sum(quantity), inventoryname, qualid'
                              ' FROM agentstateinventories'
                              ' INNER JOIN resources'
                              ' ON resources.resourceid'
                              ' = agentstateinventories.resourceid'
                              ' WHERE agentstateinventories.agentid'
                              ' = """ + str(agent) + """ GROUP BY'
                              ' inventoryname').fetchall()
        for stream in stkpile:
            masses = cur.execute('SELECT qualid, nucid, massfrac '
                                 'FROM compositions '
                                 'WHERE qualid = ' +
                                 str(stream['qualid'])).fetchall()

            outstring += ('Stream ' + str(count) +
                          ' Total = ' + str(stream['sum(quantity)']) +
                          ' kg \n')
            for isotope in masses:
                outstring += (str(isotope['nucid']) + ' = ' +
                              str(isotope['massfrac'] *
                                  stream['sum(quantity)']) +
                              ' kg \n')
            outstring += '\n'
            count += 1
        outstring += '\n'
    outstring += '\n'

    return outstring


def fuel_into_reactors(cur):
    """ Finds timeseries of mass of fuel received by reactors

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor

    Returns
    -------
    timeseries list of fuel into reactors [tons]
    """
    init_year, init_month, duration, timestep = get_timesteps(cur)
    fuel = cur.execute('SELECT time, sum(quantity) FROM transactions '
                       'INNER JOIN resources ON '
                       'resources.resourceid = transactions.resourceid '
                       'INNER JOIN agententry ON '
                       'transactions.receiverid = agententry.agentid '
                       'WHERE spec LIKE "%Reactor%" '
                       'GROUP BY time').fetchall()

    return get_timeseries_cum(fuel, duration, True)


def u_util_calc(cur):
    """ Returns fuel utilization factor of fuel cycle

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor

    Returns
    -------
    u_util_timeseries: numpy array
        Timeseries of Uranium utilization factor
    Prints simulation average Uranium Utilization
    """
    # timeseries of natural uranium
    u_supply_timeseries = np.array(nat_u_timeseries(cur))

    # timeseries of fuel into reactors
    fuel_timeseries = np.array(fuel_into_reactors(cur))

    # timeseries of Uranium utilization
    u_util_timeseries = np.nan_to_num(fuel_timeseries / u_supply_timeseries)
    print('The Average Fuel Utilization Factor is: ')
    print(sum(u_util_timeseries) / len(u_util_timeseries))

    return u_util_timeseries


def where_comm(cur, commodity, prototypes):
    """ Returns dict of where a commodity is from

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    commodity: str
        name of commodity
    prototypes: list
        list of prototypes that provide the commodity

    Returns
    -------
    trade_dict: dictioary
        "dictionary with key=prototype name, and
        value=timeseries list of commodity sent from prototypes"
    """
    init_year, init_month, duration, timestep = get_timesteps(cur)
    query = ('SELECT time, sum(quantity) FROM transactions '
             'INNER JOIN resources ON resources.resourceid = '
             'transactions.resourceid WHERE commodity = "' +
             str(commodity) + '" AND senderid '
             '= 9999 GROUP BY time')
    trade_dict = collections.OrderedDict()
    for agent in prototypes:
        agent_id = get_prototype_id(cur, agent)
        from_agent = cur.execute(query.replace(
            '9999', ' OR senderid = '.join(agent_id))).fetchall()
        trade_dict[agent] = get_timeseries_cum(from_agent, duration, True)

    return trade_dict


def get_waste_dict(isotope_list, mass_list, time_list, duration):
    """Given an isotope, mass and time list, creates a dictionary
       With key as isotope and time series of the isotope mass.

    Parameters
    ----------
    isotope_list: list
        list with all the isotopes from resources table
    mass_list: list
        list with all the mass values from resources table
    time_list: list
        list with all the time values from resources table
    duration: int
        simulation duration

    Returns
    -------
    waste_dict: dictionary
        dictionary with "key=isotope, and
        value=mass timeseries of each unique isotope"
    """
    waste_dict = collections.OrderedDict()
    isotope_set = set(isotope_list)
    for iso in isotope_set:
        mass = 0
        time_mass = []
        # at each timestep,
        for i in range(0, duration):
            # for each element in database,
            for x, y in enumerate(isotope_list):
                if i == time_list[x] and y == iso:
                    mass += mass_list[x]
            time_mass.append(mass)
        waste_dict[iso] = time_mass

    return waste_dict


def capacity_calc(governments, timestep, entry, exit_step):
    """Adds and subtracts capacity over time for plotting

    Parameters
    ----------
    governments: list
        list of governments (countries)
    timestep: np.linspace
        list of timestep from 0 to simulation time
    entry: list
        power_cap, agentid, parentid, entertime
        of all entered reactors
    exit_step: list
        power_cap, agentid, parenitd, exittime
        of all decommissioned reactors

    Returns
    -------
    power_dict: dictionary
        "dictionary with key=government, and
        value=timeseries list capacity"
    """
    power_dict = collections.OrderedDict()
    for gov in governments:
        capacity = []
        cap = 0
        for t in timestep:
            for enter in entry:
                if (enter['entertime'] == t and
                        enter['parentid'] == gov['agentid']):
                    cap += enter['max(value)'] * 0.001
            for dec in exit_step:
                if (dec['exittime'] == t and
                        dec['parentid'] == gov['agentid']):
                    cap -= dec['max(value)'] * 0.001
            capacity.append(cap)
        power_dict[gov['prototype']] = np.asarray(capacity)

    return power_dict


def reactor_deployments(governments, timestep, entry, exit_step):
    """Adds and subtracts number of reactors deployed over time
    for plotting

    Parameters
    ----------
    governments: list
        list of governments (countries)
    timestep: np.linspace
        list of timestep from 0 to simulation time
    entry: list
        power_cap, agentid, parentid, entertime
        of all entered reactors

    exit_step: list
        power_cap, agentid, parenitd, exittime
        of all decommissioned reactors

    Returns
    -------
    deployment: dictionary
        "dictionary with key=government, and
        value=timeseries number of reactors"
    """
    deployment = collections.OrderedDict()
    for gov in governments:
        num_reactors = []
        count = 0
        for t in timestep:
            for enter in entry:
                if (enter['entertime'] == t and
                        enter['parentid'] == gov['agentid']):
                    count += 1
            for dec in exit_step:
                if (dec['exittime'] == t and
                        dec['parentid'] == gov['agentid']):
                    count -= 1
            num_reactors.append(count)
        deployment[gov['prototype']] = np.asarray(num_reactors)

    return deployment


def multi_line_plot(dictionary, timestep,
                    xlabel, ylabel, title,
                    outputname, init_year):
    """ Creates a multi-line plot of timestep vs dictionary

    Parameters
    ----------
    dictionary: dictionary
        dictionary with "key=description of timestep, and
        value=list of timestep progressions"
    timestep: numpy linspace
        timestep of simulation
    xlabel: str
        xlabel of plot
    ylabel: str
        ylabel of plot
    title: str
        title of plot
    init_year: int
        initial year of simulation

    Returns
    -------
    """
    # set different colors for each bar
    color_index = 0
    # for every country, create bar chart with different color
    for key in dictionary:
        # label is the name of the nuclide (converted from ZZAAA0000 format)
        if isinstance(key, str) is True:
            label = key.replace('_government', '')
        else:
            label = str(key)

        plt.plot(timestep_to_years(init_year, timestep),
                 dictionary[key],
                 label=label)
        color_index += 1
        if sum(sum(dictionary[k]) for k in dictionary) > 1000:
            ax = plt.gca()
            ax.get_yaxis().set_major_formatter(
                plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.legend(loc=(1.0, 0), prop={'size': 10})
        plt.grid(True)
        plt.savefig(outputname + '_' + label + '.png',
                    format='png',
                    bbox_inches='tight')
        plt.close()


def stacked_bar_chart(dictionary, timestep,
                      xlabel, ylabel, title,
                      outputname, init_year):
    """ Creates stacked bar chart of timstep vs dictionary

    Parameters
    ----------
    dictionary: dictionary
        dictionary with value: timeseries data
    timestep: numpy linspace
        list of timestep (x axis)
    xlabel: str
        xlabel of plot
    ylabel: str
        ylabel of plot
    title: str
        title of plot
    init_year: int
        simulation start year

    Returns
    -------
    """
    # set different colors for each bar
    color_index = 0
    top_index = True
    prev = np.zeros(1)
    plot_list = []
    # for every country, create bar chart with different color
    for key in dictionary:
        if isinstance(key, str) is True:
            label = key.replace('_government', '')
        else:
            label = str(key)
        # very first country does not have a 'bottom' argument
        if sum(dictionary[key]) == 0:
            print(label + ' has no values')
        elif top_index is True:
            plot = plt.bar(left=timestep_to_years(init_year, timestep),
                           height=dictionary[key],
                           width=0.1,
                           color=cm.viridis(
                float(color_index) / len(dictionary)),
                edgecolor='none',
                label=label)
            prev = dictionary[key]
            top_index = False
            plot_list.append(plot)

        # All curves except the first have a 'bottom'
        # defined by the previous curve
        else:
            plot = plt.bar(left=timestep_to_years(init_year, timestep),
                           height=dictionary[key],
                           width=0.1,
                           color=cm.viridis(
                float(color_index) / len(dictionary)),
                edgecolor='none',
                bottom=prev,
                label=label)
            prev = np.add(prev, dictionary[key])
            plot_list.append(plot)

        color_index += 1

    # plot
    if sum(sum(dictionary[k]) for k in dictionary) > 1000:
        ax = plt.gca()
        ax.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xlabel(xlabel)
    if len(dictionary) > 1:
        plt.legend(loc=(1.0, 0))
    plt.grid(True)
    plt.savefig(outputname + '.png', format='png', bbox_inches='tight')
    plt.close()


def plot_power(cur):
    """ Gets capacity vs time for every country
        in stacked bar chart.

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor

    Returns
    -------
    """
    init_year, init_month, duration, timestep = get_timesteps(cur)
    power_dict = get_power_dict(cur)
    stacked_bar_chart(power_dict, timestep,
                      'Years', 'Net_Capacity [GWe]',
                      'Net Capacity vs Time',
                      'power_plot', init_year)

    deployment_dict = get_deployment_dict(cur)
    stacked_bar_chart(deployment_dict, timestep,
                      'Years', 'Number of Reactors',
                      'Number of Reactors vs Time',
                      'num_plot', init_year)


def plot_in_out_flux(cur, facility, influx_bool, title, outputname):
    """plots timeseries influx/ outflux from facility name in kg.

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    facility: str
        facility name
    influx_bool: bool
        if true, calculates influx,
        if false, calculates outflux
    title: str
        title of the multi line plot
    outputname: str
        filename of the multi line plot file

    Returns
    -------
    """
    agent_ids = get_agent_ids(cur, facility)
    if influx_bool is True:
        resources = cur.execute(exec_string(agent_ids,
                                            'transactions.receiverId',
                                            'time, sum(quantity), '
                                            'qualid') +
                                ' GROUP BY time, qualid').fetchall()
    else:
        resources = cur.execute(exec_string(agent_ids,
                                            'transactions.senderId',
                                            'time, sum(quantity), '
                                            'qualid') +
                                ' GROUP BY time, qualid').fetchall()

    compositions = cur.execute('SELECT qualid, nucid, massfrac '
                               'FROM compositions').fetchall()

    init_year, init_month, duration, timestep = get_timesteps(cur)
    transactions = get_isotope_transactions(resources, compositions)
    waste_dict = get_waste_dict(transactions.keys(),
                                transactions.values()[0],
                                transactions.values()[1],
                                duration)

    if influx_bool is False:
        stacked_bar_chart(waste_dict, timestep,
                          'Years', 'Mass [kg]',
                          title, outputname, init_year)
    else:
        multi_line_plot(waste_dict, timestep,
                        'Years', 'Mass [kg]',
                        title, outputname, init_year)


def source_throughput(cur, duration, frac_prod, frac_tail):
    """ Calculates throughput required for nat_u source before enrichment
    by calculating the average mass of fuel gone into reactors over
    simulation. Assuming natural uranium is put as feed

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    duration: int
        duration of simulation
    frac_prod: float
        mass fraction of U235 in fuel after enrichment in decimals
    frac_tail: float
        mass fraction of U235 in tailings after enrichment in decimals

    Returns
    -------
    throughput: float
        appropriate nat_u throughput for source
    """
    avg_fuel_used = fuel_into_reactors(cur)[-1] * 1000 / duration
    feed_factor = (frac_prod - frac_tail) / (0.00711 - frac_tail)
    print('Throughput should be at least: ' +
          str(feed_factor * avg_fuel_used) + ' [kg]')
    return feed_factor * avg_fuel_used


def import_csv(in_csv, delimit):
    """ Imports contents of a comma delimited csv file
    to a 2D list.

    Parameters
    ---------
    in_csv: str
        csv file name.
    delimit: str
        delimiter of the csv file

    Returns
    -------
    data_list: list
        list with fleetcomp data.
    """
    with open(in_csv, 'r') as source:
        sourcereader = csv.reader(source, delimiter=delimit)
        data_list = []
        for row in sourcereader:
            data_list.append(row)
    return data_list


def get_cf(in_list):
    """ Creates a list of capacity factor from
    the imported csv file

    Parameters
    ----------
    in_list: list
        list containing data stored in a csv file

    Returns
    -------
    cf: list
        list of capacity factors per month
    """
    cf = []
    for row in in_list[1:]:
        for i in range(0, 12):
            cf.append(float(row[1]) / 100)

    return cf


def get_generation(in_list):
    """ Creates a list of power generated from
    the imported csv file

    Parameters
    ----------
    in_list: list
        list containing data stored in a csv file

    Returns
    -------
    generation: list
        list of power generated per month
    """
    generation = []
    for row in in_list[1:]:
        for i in range(0, 12):
            generation.append(float(row[2]) / 1000)

    return generation
