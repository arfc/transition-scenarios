import collections
import numpy as np
import matplotlib.pyplot as plt
import sqlite3 as lite
import sys
from itertools import cycle
import matplotlib
from matplotlib import cm
from pyne import nucname


if len(sys.argv) < 2:
    print('Usage: python analysis.py [cylus_output_file]')


def cursor(file_name):
    """Connects and returns a cursor to an sqlite output file

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


def agent_ids(cur, archetype):
    """Gets all agentids from Agententry table for wanted archetype

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
    agentids: list
        list of all agentId strings
    """
    agents = cur.execute("SELECT agentid FROM agententry WHERE spec "
                         "LIKE '%" + archetype + "%' COLLATE NOCASE"
                         ).fetchall()

    return list(str(agent['agentid']) for agent in agents)


def prototype_id(cur, prototype):
    """Returns agentid of a prototype

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    prototype: str
        name of prototype

    Returns
    -------
    agent_id: list
        list of prototype agentids as strings
    """
    ids = cur.execute('SELECT agentid FROM agententry '
                      'WHERE prototype = "' +
                      str(prototype) + '" COLLATE NOCASE').fetchall()

    return list(str(agent['agentid']) for agent in ids)


def institutions(cur):
    """Returns prototype and agentids of institutions

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
    """Returns list of years in simulation

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


def exec_string(specific_search, search, request_colmn):
    """Generates sqlite query command to select things and
        inner join resources and transactions.

    Parameters
    ----------
    specific_search: list
        list of items to specify search
        This variable will be inserted as sqlite
        query arugment following the search keyword
    search: str
        criteria for specific_search search
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
    if len(specific_search) == 0:
        raise Exception('Cannot create an exec_string with an empty list')
    if isinstance(specific_search[0], str):
        specific_search = ['"' + x + '"' for x in specific_search]

    query = ("SELECT " + request_colmn +
             " FROM resources INNER JOIN transactions"
             " ON transactions.resourceid = resources.resourceid"
             " WHERE (" + str(search) + ' = ' + str(specific_search[0])
             )
    for item in specific_search[1:]:
        query += ' OR ' + str(search) + ' = ' + str(item)
    query += ')'

    return query


def simulation_timesteps(cur):
    """Returns simulation start year, month, duration and
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


def timeseries(specific_search, duration, kg_to_tons):
    """returns a timeseries list from specific_search data.

    Parameters
    ----------
    specific_search: list
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
    timeseries list of commodities stored in specific_search
    """
    value = 0
    value_timeseries = []
    array = np.array(specific_search)
    if len(specific_search) > 0:
        for i in range(0, duration):
            value = sum(array[array[:, 0] == i][:, 1])
            if kg_to_tons:
                value_timeseries.append(value * 0.001)
            else:
                value_timeseries.append(value)
    return value_timeseries


def timeseries_cum(specific_search, duration, kg_to_tons):
    """returns a timeseries list from specific_search data.

    Parameters
    ----------
    specific_search: list
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
    array = np.array(specific_search)
    if len(specific_search) > 0:
        for i in range(0, duration):
            value += sum(array[array[:, 0] == i][:, 1])
            if kg_to_tons:
                value_timeseries.append(value * 0.001)
            else:
                value_timeseries.append(value)
    return value_timeseries


def isotope_transactions(resources, compositions):
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


def facility_commodity_flux(cur, agentids,
                            facility_commodities, is_outflux,
                            is_cum=True):
    """Returns dictionary of commodity in/outflux from agents

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    agentids: list
        list of agentids
    facility_commodities: list
        list of commodities
    is_outflux: bool
        gets outflux if True, influx if False
    is_cum: bool
        gets cumulative timeseris if True, monthly value if False

    Returns
    -------
    commodity_region: dictionary
        dictionary with "key=commodity, and
        value=timeseries list of masses in kg"
    """
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    commodity_region = collections.OrderedDict()
    for comm in facility_commodities:
        query = (exec_string(agentids, 'receiverid',
                             'time, sum(quantity), qualid') +
                 ' and (commodity = "' + str(comm) +
                 '") GROUP BY time')
        # outflux changes receiverid to senderid
        if is_outflux:
            query = query.replace('receiverid', 'senderid')

        res = cur.execute(query).fetchall()
        if is_cum:
            commodity_region[comm] = timeseries_cum(res, duration, True)
        else:
            commodity_region[comm] = timeseries(res, duration, True)

    return commodity_region


def commodity_flux_region(cur, agentids, commodities,
                          is_outflux, is_cum=True):
    """Returns dictionary of timeseries of all the commodity outflux,
        that is either coming in/out of the agent
        separated by region

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    agentids: list
        list of agentids
    commodities: list
        list of commodities to include
    is_outflux: bool
        gets outflux from agent if True
        gets influx to agent if False
    is_cum: bool
        gets cumulative timeseris if True, monthly value if False

    Returns
    -------
    commodity_region: dictionary
        dictionary with "key=region, and
        value= timeseries list of masses in kg"
    """
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    commodity_region = collections.OrderedDict()
    commodities = ['"' + x + '"' for x in commodities]
    query = ('SELECT time, sum(quantity), parentid '
             'FROM transactions '
             'INNER JOIN resources '
             'ON resources.resourceid = '
             'transactions.resourceid '
             'INNER JOIN agententry '
             'ON agententry.agentid = transactions.SENDERID '
             'WHERE (commodity = ' +
             ' OR commodity = '.join(commodities) + ') AND ('
             'receiverid = ' +
             ' OR receiverid = '.join(agentids) + ') GROUP BY '
             'time, parentid')
    if is_outflux:
        query = query.replace('receiverid', 'senderid')
        query = query.replace('SENDERID', 'RECEIVERID')
    resources = cur.execute(query).fetchall()
    govs = cur.execute('SELECT agentid, prototype FROM agententry '
                       'WHERE kind = "Inst"').fetchall()
    for gov in govs:
        from_gov = [(x['time'], x['sum(quantity)'])
                    for x in resources if x['parentid'] == gov['agentid']]
        if is_cum:
            commodity_region[gov['prototype']] = timeseries_cum(
                from_gov, duration, True)
        else:
            commodity_region[gov['prototype']] = timeseries(
                from_gov, duration, True)
    return commodity_region


def facility_commodity_flux_isotopics(cur, agentids,
                                      facility_commodities, is_outflux, is_cum=True):
    """Returns timeseries isotoptics of commodity in/outflux
    from agents

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    agentids: list
        list of agentids
    facility_commodities: list
        list of commodities
    is_outflux: bool
        gets outflux if True, influx if False
    is_cum: bool
        gets cumulative timeseris if True, monthly value if False

    Returns
    -------
    isotope_timeseries: dictionary
        dictionary with "key=isotope, and
        value=timeseries list of masses in kg"
    """
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    isotope_timeseries = collections.defaultdict(list)
    for comm in facility_commodities:
        query = ('SELECT time, sum(quantity)*massfrac, nucid '
                 'FROM transactions INNER JOIN resources '
                 'ON resources.resourceid = transactions.resourceid '
                 'LEFT OUTER JOIN compositions '
                 'ON compositions.qualid = resources.qualid '
                 'WHERE (receiverid = ' +
                 ' OR receiverid = '.join(agentids) +
                 ') AND (commodity = "' + str(comm) +
                 '") GROUP BY time, nucid')
        # outflux changes receiverid to senderid
        if is_outflux:
            query = query.replace('receiverid', 'senderid')

        res = cur.execute(query).fetchall()
        for time, amount, nucid in res:
            isotope_timeseries[nucname.name(nucid)].append((time, amount))
    for key in isotope_timeseries:
        if is_cum:
            isotope_timeseries[key] = timeseries_cum(isotope_timeseries[key], duration, True)
        else:
            isotope_timeseries[key] = timeseries(isotope_timeseries[key], duration, True)
    return isotope_timeseries


def stockpiles(cur, facility, is_cum=True):
    """gets inventory timeseries in a fuel facility

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    facility: str
        name of facility
    is_cum: bool
        gets cumulative timeseris if True, monthly value if False

    Returns
    -------
    pile: dictionary
        dictionary with "key=agent type, and
        value=timeseries list of stockpile"
    """
    pile = collections.OrderedDict()
    agentid = agent_ids(cur, facility)
    query = exec_string(agentid, 'agentid', 'timecreated, quantity, qualid')
    query = query.replace('transactions', 'agentstateinventories')
    stockpile = cur.execute(query).fetchall()
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    if is_cum:
        stock_timeseries = timeseries_cum(stockpile, duration, True)
    else:
        stock_timeseries = timeseries(stockpile, duration, True)
    pile[facility] = stock_timeseries

    return pile


def swu_timeseries(cur, is_cum=True):
    """returns dictionary of swu timeseries for each enrichment plant

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    is_cum: bool
        gets cumulative timeseris if True, monthly value if False

    Returns
    -------
    swu: dictionary
        dictionary with "key=Enrichment (facility number), and
        value=swu timeseries list"
    """
    swu = collections.OrderedDict()
    agentid = agent_ids(cur, 'Enrichment')
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    for num in agentid:
        swu_data = cur.execute('SELECT time, value '
                               'FROM timeseriesenrichmentswu '
                               'WHERE agentid = ' + str(num)).fetchall()
        if is_cum:
            swu_timeseries = timeseries_cum(swu_data, duration, False)
        else:
            swu_timeseries = timeseries(swu_data, duration, False)

        swu['Enrichment_' + str(num)] = swu_timeseries

    return swu


def power_capacity(cur):
    """Gets dictionary of power capacity by calling capacity_calc

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor

    Returns
    ------
    power: dictionary
        "dictionary with key=government, and
        value=timeseries list of installed capacity"
    """
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    governments = institutions(cur)

    # get power cap values
    entry_exit = cur.execute('SELECT max(value), timeseriespower.agentid, '
                             'parentid, entertime, entertime + lifetime'
                             ' FROM agententry '
                             'INNER JOIN timeseriespower '
                             'ON agententry.agentid = timeseriespower.agentid '
                             'GROUP BY timeseriespower.agentid').fetchall()

    return capacity_calc(governments, timestep, entry_exit)


def power_capacity_of_region(cur, region_name):
    """Gets dictionary of power capacity of a specific region

    Parameters
    ----------
    cur: sqlite cursor
    region_name: str
        name of region to serach for

    Returns
    -------
    power: dictionary
        "dictionary with key=government and
        value=timeseries list of installed capacity"
    """
    parentid = cur.exectue('SELECT agentid FROM agententry WHERE '
                           'Prototype LIKE "%' + region_name + '%" '
                           'AND Kind = "Inst"').fetchone()

    entry_exit = cur.execute('SELECT max(value), timeseriespower.agentid, '
                             'parentid, entrytime, entertime + lifetime'
                             ' FROM agententry '
                             'INNER JOIN timeseriespower '
                             'ON agententry.agentid = timeseriespower.agentid '
                             'GROUP BY timeseriespower.agentid '
                             'WHERE parentid = %i' % parentid[0]).fetchall()


def deployments(cur):
    """Gets dictionary of reactors deployed over time
    by calling reactor_deployments

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor

    Returns
    ------
    deployment_government: dictionary
        "dictionary with key=government, and
        value=timeseries list of number of reactors"
    """
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    governments = institutions(cur)

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


def fuel_usage_timeseries(cur, fuels, is_cum=True):
    """Calculates total fuel usage over time

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    fuels: list
        list of fuel commodity names (eg. uox, mox) as string
        to consider in fuel usage.
    is_cum: bool
        gets cumulative timeseris if True, monthly value if False

    Returns
    -------
    fuel_usage: dictionary
        dictionary with "key=fuel (from fuels),
        value=timeseries list of fuel amount [kg]"
    """
    fuel_usage = collections.OrderedDict()
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    for fuel in fuels:
        temporary_fuels = [fuel]
        fuel_quantity = cur.execute(exec_string(temporary_fuels, 'commodity',
                                                'time, sum(quantity)') +
                                    ' GROUP BY time').fetchall()
        quantity_timeseries = []
        try:
            if is_cum:
                quantity_timeseries = timeseries_cum(
                    fuel_quantity, duration, True)
            else:
                quantity_timeseries = timeseries(
                    fuel_quantity, duration, True)
            fuel_usage[fuel] = quantity_timeseries
        except:
            print(str(fuel) + ' has not been used.')

    return fuel_usage


def nat_u_timeseries(cur, is_cum=True):
    """Finds natural uranium supply from source
        Since currently the source supplies all its capacity,
        the timeseriesenrichmentfeed is used.

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    is_cum: bool
        gets cumulative timeseris if True, monthly value if False

    Returns
    -------
    timeseries: function
        calls a function that returns timeseries list of natural U
        demand from enrichment [MTHM]
    """
    init_year, init_month, duration, timestep = simulation_timesteps(cur)

    # Get Nat U feed to enrichment from timeseriesenrichmentfeed
    feed = cur.execute('SELECT time, sum(value) '
                       'FROM timeseriesenrichmentfeed '
                       'GROUP BY time').fetchall()
    if is_cum:
        return timeseries_cum(feed, duration, True)
    else:
        return timeseries(feed, duration, True)


def trade_timeseries(cur, sender, receiver,
                   is_prototype, do_isotopic,
                   is_cum=True):
    """Returns trade timeseries between two prototypes' or facilities
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
    is_cum: bool
        gets cumulative timeseris if True, monthly value if False

    Returns:
    --------
    trades: dictionary
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
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    isotope_timeseries = collections.defaultdict(list)
    trades = collections.defaultdict()

    if is_prototype:
        sender_id = prototype_id(cur, sender)
        receiver_id = prototype_id(cur, receiver)
    else:
        sender_id = agent_ids(cur, sender)
        receiver_id = agent_ids(cur, receiver)

    if do_isotopic:
        trade = cur.execute('SELECT time, sum(quantity)*massfrac, nucid '
                            'FROM transactions INNER JOIN resources ON '
                            'resources.resourceid = transactions.resourceid '
                            'LEFT OUTER JOIN compositions '
                            'ON compositions.qualid = resources.qualid '
                            'WHERE (senderid = ' +
                            ' OR senderid = '.join(sender_id) +
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
                            ') GROUP BY time').fetchall(
        )
    if do_isotopic:
        for time, amount, nucid in trade:
            isotope_timeseries[nucname.name(nucid)].append((time, amount))
        for key in isotope_timeseries:
            if is_cum:
                isotope_timeseries[key] = timeseries_cum(
                    isotope_timeseries[key], duration, True)
            else:
                isotope_timeseries[key] = timeseries(isotope_timeseries[key], duration, True)
        return isotope_timeseries
    else:
        key_name = str(sender)[:5] + ' to ' + str(receiver)[:5]
        if is_cum:
            trades[key_name] = timeseries_cum(trade, duration, True)
        else:
            trades[key_name] = timeseries(trade, duration, True)
        return trades


def final_stockpile(cur, facility):
    """get final stockpile in a fuel facility

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    facility: str
        name of facility

    Returns
    -------
    mthm_stockpile: str
        MTHM value of stockpile
    """
    agentid = agent_ids(cur, facility)
    mthm_stockpile = ''
    for agent in agentid:
        count = 1
        name = cur.execute('SELECT prototype FROM agententry'
                           'WHERE agentid = ' + str(agent)).fetchone()

        mthm_stockpile += 'The Stockpile in ' + str(name[0]) + ' : \n \n'
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

            mthm_stockpile += ('Stream ' + str(count) +
                          ' Total = ' + str(stream['sum(quantity)']) +
                          ' kg \n')
            for isotope in masses:
                mthm_stockpile += (str(isotope['nucid']) + ' = ' +
                              str(isotope['massfrac'] *
                                  stream['sum(quantity)']) +
                              ' kg \n')
            mthm_stockpile += '\n'
            count += 1
        mthm_stockpile += '\n'
    mthm_stockpile += '\n'

    return mthm_stockpile


def fuel_into_reactors(cur, is_cum=True):
    """Finds timeseries of mass of fuel received by reactors

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    is_cum: bool
        gets cumulative timeseris if True, monthly value if False

    Returns
    -------
    timeseries list of fuel into reactors [tons]
    """
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    fuel = cur.execute('SELECT time, sum(quantity) FROM transactions '
                       'INNER JOIN resources ON '
                       'resources.resourceid = transactions.resourceid '
                       'INNER JOIN agententry ON '
                       'transactions.receiverid = agententry.agentid '
                       'WHERE spec LIKE "%Reactor%" '
                       'GROUP BY time').fetchall()

    if is_cum:
        return timeseries_cum(fuel, duration, True)
    else:
        return timeseries(fuel, duration, True)


def u_util_calc(cur):
    """Returns fuel utilization factor of fuel cycle

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
    fuel_usage = np.array(fuel_into_reactors(cur))

    # timeseries of Uranium utilization
    u_util_timeseries = np.nan_to_num(fuel_usage / u_supply_timeseries)
    print('The Average Fuel Utilization Factor is: ')
    print(sum(u_util_timeseries) / len(u_util_timeseries))

    return u_util_timeseries


def commodity_origin(cur, commodity, prototypes, is_cum=True):
    """Returns dict of where a commodity is from

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
    prototype_trades: dictioary
        "dictionary with key=prototype name, and
        value=timeseries list of commodity sent from prototypes"
    """
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    query = ('SELECT time, sum(quantity) FROM transactions '
             'INNER JOIN resources ON resources.resourceid = '
             'transactions.resourceid WHERE commodity = "' +
             str(commodity) + '" AND senderid '
             '= 9999 GROUP BY time')
    prototype_trades = collections.OrderedDict()
    for agent in prototypes:
        agent_id = prototype_id(cur, agent)
        from_agent = cur.execute(query.replace(
            '9999', ' OR senderid = '.join(agent_id))).fetchall()
        if is_cum:
            prototype_trades[agent] = timeseries_cum(from_agent, duration, True)
        else:
            prototype_trades[agent] = timeseries(from_agent, duration, True)
    return prototype_trades


def commodity_per_institution(cur, commodity, timestep=10000):
    """Outputs outflux of commodity per institution
        before timestep

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    commodity: str
        commodity to search for

    Returns
    -------
    institution_output: dictionary
        key = institution
        value = timeseries list of outflux of commodity
    """

    institutes = institutions(cur)
    institution_output = collections.OrderedDict()
    for inst in institutes:
        inst_id = inst[1]
        inst_name = inst[0]
        facilities = cur.execute('SELECT agentid FROM agententry '
                                 'WHERE parentid = ' + str(inst_id)).fetchall()
        facilities_collected = []
        for fac in facilities:
            facilities_collected.append(fac[0])
        query = exec_string(facilities_collected, 'senderid', 'sum(quantity)')
        query += ' AND commodity = "' + commodity + \
            '" and time < ' + str(timestep)
        institution_output[inst_name] = cur.execute(query).fetchone()[0]

    return institution_output


def wastes(isotopes, mass_timeseries, duration):
    """Given an isotope, mass and time list, creates a dictionary
       With key as isotope and time series of the isotope mass.
    
    Inputs:
    isotopes: list
        list with all the isotopes from resources table
    mass_timeseries: list
        a list of lists.  each outer list corresponds to a different isotope
        and contains tuples in the form (time,mass) for the isotope transaction.
    duration: integer
        simulation duration
    
    Outputs:
    waste: dictionary
        dictionary with "key=isotope, and
        value=mass timeseries of each unique isotope"
    """
    
    # first, the individual key strings are pulled into an array, which makes it easier to use them later
    keys = []
    for key in isotopes:
        keys.append(key)
    
    #initialize waste
    waste = {}
        
    # the next steps are the same for any number of isotopes in the recipe, but
    # if there is more than one, a loop is added to accommodate having multple isotopes.
    
    # this function, in practice, is called using the data from the isotope_transactions
    # function.  If you look at this data, you will notice that when there was no
    # event, i.e., no influx or outflux of material, the data point for that time step does not exist.
    # this is not particularly helpful for plotting data.  The steps below pull out the time and mass
    # values from within the tuple, and create separate arrays of each (called times and masses, respectively)
    # then, in order to "fill in" the data points in which there were no events, new arrays, called time_developed
    # masses1, are created.  An empty array called nums is also made, which is the length of the simulation duration.
    # then, a loop is used to check if the timestep in nums is already in time_developed.  If it is not, the .insert function
    # is used to put the data point into the correct position, and similarly, a data point is inserted in masses1 in
    # this position, with a value of 0
    if len(mass_timeseries) == 1:
        times = []
        masses = []
        for i in list(mass_timeseries[0]):
            time = str(i).split(',')[0]
            times.append((float(time.strip('('))))
            mass = str(i).split(',')[1]
            masses.append((float(mass.strip(')').strip('('))))
    
    
        time_developed = times
        masses1 = masses
        nums = np.arange(0, duration)

        for j in nums:
            if j not in time_developed:
                time_developed.insert(j, j) 
                masses1.insert(j,0)
                
        waste[key] = masses1
            
    else:
        for element in range(len(mass_timeseries)):
            times = []
            masses = []
            for i in list(mass_timeseries[element]):
                time = str(i).split(',')[0]
                times.append((float(time.strip('('))))
                mass = str(i).split(',')[1]
                masses.append((float(mass.strip(')').strip('('))))
    
    
            time_developed = times
            masses1 = masses
            nums = np.arange(0,duration)

            for j in nums:
                if j not in time_developed:
                    time_developed.insert(j, j) 
                    masses1.insert(j,0)
                        
            waste[keys[element]] = masses1
    
    return waste



def capacity_calc(governments, timestep, entry_exit):
    """Adds and subtracts capacity over time for plotting

    Parameters
    ----------
    governments: list
        list of governments (countries)
    timestep: np.linspace
        list of timestep from 0 to simulation time
    entry_exit: list
        power_cap, agentid, parentid, entertime, exittime
        of all entered reactors

    Returns
    -------
    power: dictionary
        "dictionary with key=government, and
        value=timeseries list capacity"
    """
    power = collections.OrderedDict()
    for gov in governments:
        capacity = []
        cap = 0
        for t in timestep:
            for agent in entry_exit:
                if (agent['entertime'] == t and
                        agent['parentid'] == gov['agentid']):
                    cap += agent['max(value)'] * 0.001
                if (agent['entertime + lifetime'] == t and
                        agent['parentid'] == gov['agentid']):
                    cap -= agent['max(value)'] * 0.001
            capacity.append(cap)
        power[gov['prototype']] = np.asarray(capacity)

    return power


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


def multiple_line_plots(dictionary, timestep,
                        xlabel, ylabel, title,
                        outputname, init_year):
    """Creates multiple line plots of timestep vs dictionary

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
        plt.savefig(label + '_' + outputname + '.png',
                    format='png',
                    bbox_inches='tight')
        plt.close()


def combined_line_plot(dictionary, timestep,
                       xlabel, ylabel, title,
                       outputname, init_year):
    """Creates a combined line plot of timestep vs dictionary

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
    plt.figure()
    # for every country, create bar chart with different color
    for key in dictionary:
        # label is the name of the nuclide (converted from ZZAAA0000 format)
        if isinstance(key, str) is True:
            label = key.replace('_government', '')
        else:
            label = str(key)

        plt.plot(timestep_to_years(init_year, timestep),
                 dictionary[key],
                 label=label,
                 color=cm.viridis(float(color_index) / len(dictionary)))
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
    plt.savefig(label + '_' + outputname + '.png',
                format='png',
                bbox_inches='tight')
    plt.close()


def double_axis_bar_line_plot(dictionary1, dictionary2, timestep,
                              xlabel, ylabel1, ylabel2,
                              title, outputname, init_year):
    """Creates a double-axis plot of timestep vs dictionary

    It is recommended that a non-cumulative timeseries is on dictionary1.

    Parameters
    ----------
    dictionary1: dictionary
        dictionary with "key=description of timestep, and
        value=list of timestep progressions"
    dictionary2: dictionary
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

    fig, ax1 = plt.subplots()
    # for every country, create bar chart with different color
    color1 = 'r'
    color2 = 'b'
    for key in dictionary1:
        # label is the name of the nuclide (converted from ZZAAA0000 format)
        if isinstance(key, str) is True:
            label = key.replace('_government', '')
        else:
            label = str(key)
        if sum(dictionary1[key]) == 0:
            print(label + ' has no values')
        else:
            ax1.bar(timestep_to_years(init_year, timestep),
                    dictionary1[key],
                    label=label,
                    color=color1)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel1, color=color1)
    ax1.tick_params('y', colors=color1)
    if sum(sum(dictionary1[k]) for k in dictionary1) > 1000:
        ax1 = plt.gca()
        ax1.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    ax2 = ax1.twinx()

    lines = ['-', '--', '-.', ':']
    linecycler = cycle(lines)
    for key in dictionary2:
        # label is the name of the nuclide (converted from ZZAAA0000 format)
        if isinstance(key, str) is True:
            label = key.replace('_government', '')
        else:
            label = str(key)

        if sum(dictionary2[key]) == 0:
            print(label + ' has no values')
        else:
            ax2.plot(timestep_to_years(init_year, timestep),
                     dictionary2[key],
                     label=label,
                     color=color2,
                     linestyle=next(linecycler))
    ax2.set_ylabel(ylabel2, color=color2)
    ax2.tick_params('y', colors=color2)

    if sum(sum(dictionary2[k]) for k in dictionary2) > 1000:
        ax2 = plt.gca()
        ax2.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

    plt.title(title)
    plt.grid(True)
    plt.savefig(label + '_' + outputname + '.png',
                format='png',
                bbox_inches='tight')
    plt.close()


def double_axis_line_line_plot(dictionary1, dictionary2, timestep,
                               xlabel, ylabel1, ylabel2,
                               title, outputname, init_year):
    """Creates a double-axis plot of timestep vs dictionary

    Parameters
    ----------
    dictionary1: dictionary
        dictionary with "key=description of timestep, and
        value=list of timestep progressions"
    dictionary2: dictionary
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
    lines = ['-', '--', '-.', ':']
    linecycler = cycle(lines)
    fig, ax1 = plt.subplots()
    top = True
    color1 = 'r'
    color2 = 'b'
    # for every country, create bar chart with different color
    for key in dictionary1:
        # label is the name of the nuclide (converted from ZZAAA0000 format)
        if isinstance(key, str) is True:
            label = key.replace('_government', '')
        else:
            label = str(key)
        if top:
            lns = ax1.plot(timestep_to_years(init_year, timestep),
                           dictionary1[key],
                           label=label,
                           color=color1,
                           linestyle=next(linecycler))
            top = False
        else:
            lns += ax1.plot(timestep_to_years(init_year, timestep),
                            dictionary1[key],
                            label=label,
                            color=color1,
                            linestyle=next(linecycler))
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel1, color=color1)
    ax1.tick_params('y', colors=color1)
    if sum(sum(dictionary1[k]) for k in dictionary1) > 1000:
        ax1 = plt.gca()
        ax1.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    ax2 = ax1.twinx()

    linecycler = cycle(lines)

    for key in dictionary2:
        # label is the name of the nuclide (converted from ZZAAA0000 format)
        if isinstance(key, str) is True:
            label = key.replace('_government', '')
        else:
            label = str(key)

        lns += ax2.plot(timestep_to_years(init_year, timestep),
                        dictionary2[key],
                        label=label,
                        color=color2,
                        linestyle=next(linecycler))
    ax2.set_ylabel(ylabel2, color=color2)
    ax2.tick_params('y', colors=color2)

    if sum(sum(dictionary2[k]) for k in dictionary2) > 1000:
        ax2 = plt.gca()
        ax2.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

    plt.title(title)
    labs = [l.get_label() for l in lns]
    plt.legend(lns, labs, loc=0, prop={'size': 10})
    plt.grid(True)
    plt.savefig(label + '_' + outputname + '.png',
                format='png',
                bbox_inches='tight')
    plt.close()


def stacked_bar_chart(dictionary, timestep,
                      xlabel, ylabel, title,
                      outputname, init_year):
    """Creates stacked bar chart of timstep vs dictionary

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
    plots = []
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
            plot = plt.bar(x=timestep_to_years(init_year, timestep),
                           height=dictionary[key],
                           width=0.5,
                           color=cm.viridis(
                float(color_index) / len(dictionary)),
                edgecolor='none',
                label=label)
            prev = dictionary[key]
            top_index = False
            plots.append(plot)

        # All curves except the first have a 'bottom'
        # defined by the previous curve
        else:
            plot = plt.bar(x=timestep_to_years(init_year, timestep),
                           height=dictionary[key],
                           width=0.5,
                           color=cm.viridis(
                float(color_index) / len(dictionary)),
                edgecolor='none',
                bottom=prev,
                label=label)
            prev = np.add(prev, dictionary[key])
            plots.append(plot)

        color_index += 1

    # plot
    if sum(sum(dictionary[k]) for k in dictionary) > 1000:
        ax = plt.gca()
        ax.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xlabel(xlabel)
    axes = plt.gca()
    if len(dictionary) > 1:
        plt.legend(loc=(1.0, 0))
    plt.grid(True)
    plt.savefig(outputname + '.png', format='png', bbox_inches='tight')
    plt.close()


def plot_power(cur):
    """Gets capacity vs time for every country
        in stacked bar chart.

    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor

    Returns
    -------
    """
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    power = power_capacity(cur)
    stacked_bar_chart(power, timestep,
                      'Years', 'Net_Capacity [GWe]',
                      'Net Capacity vs Time',
                      'power_plot', init_year)

    deployments = deployments(cur)
    stacked_bar_chart(deployments, timestep,
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
    agentids = agent_ids(cur, facility)
    if influx_bool is True:
        resources = cur.execute(exec_string(agentids,
                                            'transactions.receiverId',
                                            'time, sum(quantity), '
                                            'qualid') +
                                ' GROUP BY time, qualid').fetchall()
    else:
        resources = cur.execute(exec_string(agentids,
                                            'transactions.senderId',
                                            'time, sum(quantity), '
                                            'qualid') +
                                ' GROUP BY time, qualid').fetchall()

    compositions = cur.execute('SELECT qualid, nucid, massfrac '
                               'FROM compositions').fetchall()

    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    transactions = isotope_transactions(resources, compositions)
    waste = wastes(transactions.keys(),
                                transactions.values()[0],
                                transactions.values()[1],
                                duration)

    if influx_bool is False:
        stacked_bar_chart(waste, timestep,
                          'Years', 'Mass [kg]',
                          title, outputname, init_year)
    else:
       multiple_line_plots(waste, timestep,
                        'Years', 'Mass [kg]',
                        title, outputname, init_year)


def entered_power(cur):
    """Returns dictionary of power entered into simulation.

    Parameters
    ---------
    cur: sqlite cursor
        sqlite cursor

    Returns
    -------
    power: dictionary
        key: 'power'
        value: timeseries of power entered (non-cumulative)
    """
    power = {}
    entered = cur.execute('SELECT entertime, max(value) FROM '
                          'agententry INNER JOIN timeseriespower '
                          'ON agententry.agentid = timeseriespower.agentid '
                          'WHERE spec LIKE "%reactor%" '
                          'GROUP BY agententry.agentid').fetchall()
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    power['power'] = timeseries(entered, duration, False)
    return power


def source_throughput(cur, duration, frac_prod, frac_tail):
    """Calculates throughput required for nat_u source before enrichment
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
