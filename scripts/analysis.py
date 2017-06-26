import collections
import numpy as np
import matplotlib.pyplot as plt
import sqlite3 as lite
import sys
from matplotlib import cm


if len(sys.argv) < 2:
    print('Usage: python analysis.py [cylus_output_file]')

"""HELPERS"""


def get_agent_ids(cursor, facility):
    """ Gets all agentIds from Agententry table for wanted facility

        agententry table has the following format:
            SimId / AgentId / Kind / Spec /
            Prototype / ParentID / Lifetime / EnterTime

    Parameters
    ----------
    cursor: cursor
        cursor for sqlite3
    facility: str
        name of facility type as described in spec

    Returns
    -------
    sink_id: list
        list of all the sink agentId values as string.
    """
    agents = cursor.execute("SELECT * FROM agententry WHERE spec LIKE '%" +
                            facility + "%' COLLATE NOCASE").fetchall()

    return list(str(agent[1]) for agent in agents)


def get_prototype_id(cursor, prototype):
    """ Returns agentid of a prototype

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor
    prototype: str
        name of prototype

    Returns
    -------
    agent_id: list
        list of agent_ids for prototype as string.
    """
    ids = cursor.execute('SELECT agentid FROM agententry '
                         'WHERE prototype = "' +
                         str(prototype) + '" COLLATE NOCASE').fetchall()

    return list(str(agent[0]) for agent in ids)


def exec_string(in_list, search, whatwant):
    """ Generates sqlite query command to select things and
        inner join resources and transactions.

    Parameters
    ----------
    in_list: list
        (search) = in_list
        list of items to specify search
    search: str
        WHERE (search)
        criteria for in_list search
    whatwant: str
        SELECT (whatwant)
        column (set of values) you want out from sqlite query

    Returns
    -------
    str
        sqlite query command.
    """
    query = ("SELECT " + whatwant +
             " FROM resources INNER JOIN transactions"
             " ON transactions.resourceid = resources.resourceid"
             " WHERE (" + str(search) + ' = ' + str(in_list[0]) + ')'
             )
    for item in in_list[1:]:
        query += ' OR (' + str(search) + ' = ' + str(item) + ')'

    return query


def get_sim_time_duration(cursor):
    """ Returns simulation start year, month, duration and
    timesteps (in numpy linspace).

    Parameters
    ----------
    cursor: sqlite cursor
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
        timeseries up to duration
    """
    info = cursor.execute('SELECT initialyear, initialmonth, '
                          'duration FROM info').fetchone()
    init_year = info[0]
    init_month = info[1]
    duration = info[2]
    timestep = np.linspace(0, info[2] - 1, num=info[2])

    return init_year, init_month, duration, timestep


def get_timeseries(in_list, duration, multiplyby, cumulative):
    """ returns a timeseries list of a given data

    Parameters
    ----------
    in_list: list
        list of data to be created into timeseries
        list[0] = time
        list[1] = value, quantity
    duration: int
        duration of the simulation
    multiplyby: int
        integer to multiply the value in the list by for
        unit conversion from kilograms
    cumulative: boolean
        determine whether returned timeseries should be
        cumulative sum over time

    Returns
    -------
    timeseries list of data
    """
    value = 0
    value_timeseries = []
    array = np.array(in_list)
    if cumulative:
        for i in range(0, duration):
            if len(array) > 0:
                value += sum(array[array[:, 0] == i][:, 1])
            value_timeseries.append(value * multiplyby)
    else:
        for i in range(0, duration):
            value = sum(array[array[:, 0] == i][:, 1])
            value_timeseries.append(value * multiplyby)

    return value_timeseries


"""GETTERS"""


def snf(cursor):
    """returns a dictionary of isotopics in sink at the end of simulation

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor

    Returns
    -------
    snf_dict: dictionary
        dirctionary with key: isotope, and value: mass
    """
    sink_id = get_agent_ids(cur, 'sink')

    # get list of sum(quantity) and qualid for snf
    snf_inventory = cursor.execute(exec_string(sink_id,
                                               'transactions.receiverId',
                                               'sum(quantity), qualid') +
                                   ' GROUP BY qualid').fetchall()
    compositions = cursor.execute('SELECT qualid, nucid, massfrac '
                                  'FROM compositions').fetchall()
    snf_dict = collections.defaultdict(float)
    for comp in compositions:
        for num in snf_inventory:
            if num[0] == comp[0]:
                snf_dict[comp[1]] += num[1] * comp[2]

    return snf_dict


def get_isotope_transactions(resources, compositions):
    """Creates a dictionary with isotope name, mass, and time

    Parameters
    ----------
    resources: list
        resource data from the resources table
        list[0]: time
        list[1]: sum(quantity)
        list[2]: qualid
    compositions: list
        composition data from the compositions table
        list[0]: qualid
        list[1]: nucid
        list[2]: massfrac

    Returns
    -------
    transactions: dictionary
        dictionary with keys as isotope and value as
        list of tuples (mass moved, time)
    """
    transactions = collections.defaultdict(list)
    for res in resources:
        for comp in compositions:
            # res_qualid = res[2]
            # comp_qualid = comp[0]
            if res[2] == comp[0]:
                # comp_nucid = comp[1]
                # res_quantity = res[1s
                # mass_frac = comp[2]
                # res_time = res[0]
                transactions[comp[1]].append((res[0], res[1] * comp[2]))

    return transactions


def commodity_in_out_facility(cursor, facility, commod_list,
                              is_outflux, is_prototype):
    """ Returns timeseries of commodity in/outflux from facility or prototype

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor
    facility: str
        facility type as shown in spec or prototype name
    commod_list: list
        list of commodities
    is_outflux: bool
        gets outflux if True, influx if False
    is_prototype: bool
        searches using prototype name if True,
        facility type if False

    Returns
    -------
    commodity_dict: dictionary
        dictionary with key: commodity, and value: timeseries list
    """
    init_year, init_month, duration, timestep = get_sim_time_duration(cursor)
    if is_prototype:
        agent_ids = get_prototype_id(cursor, facility)
    else:
        agent_ids = get_agent_ids(cursor, facility)
    commodity_dict = collections.OrderedDict()
    for comm in commod_list:
        if is_outflux:
            res = cursor.execute(exec_string(agent_ids, 'senderid',
                                             'time, sum(quantity)') +
                                 ' and commodity = ' + str(comm) +
                                 ' GROUP BY time').fetchall()
        else:
            res = cursor.execute(exec_string(agent_ids, 'receiverid',
                                             'time, sum(quantity)') +
                                 ' and commodity = ' + str(comm) +
                                 ' GROUP BY time').fetchall()
        timeseries = get_timeseries(res, duration, 0.001, True)
        commodity_dict[comm] = timeseries

    return commodity_dict


def get_stockpile(cursor, facility):
    """ gets inventory timeseries in a fuel facility

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor
    facility: str
        name of facility

    Returns
    -------
    pile_dict: dictionary
        dictionary with key: facility, value: timeseries of stockpile
    """
    pile_dict = collections.OrderedDict()
    agentid = get_agent_ids(cursor, facility)
    query = exec_string(agentid, 'agentid', 'timecreated, quantity, qualid')
    query = query.replace('transactions', 'agentstateinventories')
    stockpile = cursor.execute(query).fetchall()
    init_year, init_month, duration, timestep = get_sim_time_duration(cursor)
    stock_timeseries = get_timeseries(stockpile, duration, .001, 'TRUE')
    pile_dict[facility] = stock_timeseries

    return pile_dict


def get_swu_dict(cursor):
    """ returns dictionary of swu timeseries for each enrichment plant

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor

    Returns
    -------
    swu_dict: dictionary
        dictionary with key: Enrichment (facility number),
        value: swu timeseries
    """
    swu_dict = collections.OrderedDict()
    agentid = get_agent_ids(cursor, 'Enrichment')
    init_year, init_month, duration, timestep = get_sim_time_duration(cursor)
    facility_num = 1
    for num in agentid:
        swu_data = cursor.execute('SELECT time, value '
                                  'FROM timeseriesenrichmentswu '
                                  'WHERE agentid = ' + str(num)).fetchall()
        swu_timeseries = get_timeseries(swu_data, duration, 1, 'TRUE')
        swu_dict['Enrichment' + str(facility_num)] = swu_timeseries
        facility_num += 1

    return swu_dict


def get_power_dict(cursor):
    """ Gets dictionary of power capcity and number of reactors
    by calling capacity_calc

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor

    Returns
    ------
    capacity_calc: function
        calls a function
    """
    init_year, init_month, duration, timestep = get_sim_time_duration(cursor)
    # get power cap values
    governments = cursor.execute('SELECT prototype, agentid FROM agententry '
                                 'WHERE kind = "Inst"').fetchall()

    entry = cursor.execute('SELECT max(value), timeseriespower.agentid, '
                           'parentid, entertime FROM agententry '
                           'INNER JOIN timeseriespower '
                           'ON agententry.agentid = timeseriespower.agentid '
                           'GROUP BY timeseriespower.agentid').fetchall()

    exit_step = cursor.execute('SELECT max(value), timeseriespower.agentid, '
                               'parentid, exittime FROM agentexit '
                               'INNER JOIN timeseriespower '
                               'ON agentexit.agentid = timeseriespower.agentid'
                               ' INNER JOIN agententry '
                               'ON agentexit.agentid = agententry.agentid '
                               'GROUP BY timeseriespower.agentid').fetchall()
    return capacity_calc(governments, timestep, entry, exit_step)


def fuel_usage_timeseries(cursor, fuel_list):
    """ Calculates total fuel usage over time

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor
    fuel_list: list
        list of fuel commodity names (eg. uox, mox) as string
        to consider in fuel usage.

    Returns
    -------
    fuel_dict: dictionary
        dictionary with key: fuel (from fuel_list),
        value: timeseries list of fuel amount [kg]
    """
    fuel_dict = collections.OrderedDict()
    for fuel in fuel_list:
        temp_list = ['"' + fuel + '"']
        fuel_quantity = cursor.execute(exec_string(temp_list, 'commodity',
                                                   'time, sum(quantity)') +
                                       ' GROUP BY time').fetchall()
        init_year, init_month, duration, timestep = get_sim_time_duration(
            cursor)
        quantity_timeseries = []
        try:
            quantity_timeseries = get_timeseries(
                fuel_quantity, duration, .001, 'TRUE')
            fuel_dict[fuel] = quantity_timeseries
        except:
            print(str(fuel) + ' has not been used.')

    return fuel_dict


def nat_u_timeseries(cursor):
    """ Finds natural uranium supply from source

            Since currently the source supplies all its capacity,
            the timeseriesenrichmentfeed is used.

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor

    Returns
    -------
    get_timeseries: function
        calls a function that returns timeseries of natural U
        demand from enrichment [MTHM]
    """
    init_year, init_month, duration, timestep = get_sim_time_duration(cursor)

    # Get Nat U feed to enrichment from timeseriesenrichmentfeed
    feed = cursor.execute('SELECT time, sum(value) '
                          'FROM timeseriesenrichmentfeed '
                          'GROUP BY time').fetchall()
    return get_timeseries(feed, duration, .001, 'TRUE')


def get_trade_dict(cursor, sender, receiver, is_prototype, do_isotopic):
    """ Returns trade timeseries between two prototypes' or facilities
    with or without isotopics

    Parameters
    ----------
    cursor: sqlite cursor
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
            dictionary with key: isotope,
            value: timeseries list of mass traded between two prototypes
        else:
            dictionary with key: string, sender to receiver,
            value: timeseries list of mass traded between two prototypes

    """
    init_year, init_month, duration, timestep = get_sim_time_duration(cursor)

    if is_prototype:
        sender_id = get_prototype_id(cursor, sender)
        receiver_id = get_prototype_id(cursor, receiver)
    else:
        sender_id = get_agent_ids(cursor, sender)
        receiver_id = get_agent_ids(cursor, receiver)

    trade = cursor.execute('SELECT time, sum(quantity), qualid '
                           'FROM transactions INNER JOIN resources ON '
                           'resources.resourceid = transactions.resourceid'
                           ' WHERE senderid = ' +
                           ' OR senderid = '.join(sender_id) +
                           ' AND receiverid = ' +
                           ' OR receiverid = '.join(receiver_id) +
                           ' GROUP BY time').fetchall()
    if do_isotopic:
        compositions = cursor.execute('SELECT qualid, nucid, massfrac '
                                      'FROM compositions').fetchall()
        iso_dict = get_isotope_transactions(trade, compositions)
        iso_dict = {key: get_timeseries(
            value, duration, 0.001, True) for key, value in iso_dict.items()}

        return iso_dict
    else:
        return_dict = collections.defaultdict()
        key_name = str(sender)[:5] + ' to ' + str(receiver)[:5]
        return_dict[key_name] = get_timeseries(
            trade, duration, 0.001, True)

        return return_dict


def final_stockpile(cursor, facility):
    """ get final stockpile in a fuel facility

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor
    facility: str
        name of facility

    Returns
    -------
    outstring: str
        MTHM value of stockpile
    """
    agentid = get_agent_ids(cursor, facility)
    outstring = ''
    for agent in agentid:
        count = 1
        name = cursor.execute('SELECT prototype FROM agententry'
                              'WHERE agentid = ' + str(agent)).fetchone()

        outstring += 'The Stockpile in ' + str(name[0]) + ' : \n \n'
        stkpile = cursor.execute('SELECT sum(quantity), inventoryname, qualid'
                                 ' FROM agentstateinventories'
                                 ' INNER JOIN resources'
                                 ' ON resources.resourceid'
                                 ' = agentstateinventories.resourceid'
                                 ' WHERE agentstateinventories.agentid'
                                 ' = """ + str(agent) + """ GROUP BY'
                                 ' inventoryname').fetchall()
        for stream in stkpile:
            masses = cursor.execute('SELECT * FROM compositions '
                                    'WHERE qualid = ' +
                                    str(stream[2])).fetchall()

            outstring += ('Stream ' + str(count) +
                          ' Total = ' + str(stream[0]) + ' kg \n')
            for isotope in masses:
                outstring += (str(isotope[2]) + ' = ' +
                              str(isotope[3] * stream[0]) + ' kg \n')
            outstring += '\n'
            count += 1
        outstring += '\n'
    outstring += '\n'

    return outstring


def fuel_into_reactors(cursor):
    """ Finds timeseries of mass of fuel received by reactors

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor

    Returns
    -------
    get_timeseries: function
        Function returns timeseries of mass of fuel into receactors [MTHM]
    """
    init_year, init_month, duration, timestep = get_sim_time_duration(cursor)
    fuel = cursor.execute('SELECT time, sum(quantity) FROM transactions '
                          'INNER JOIN resources ON '
                          'resources.resourceid = transactions.resourceid '
                          'INNER JOIN agententry ON '
                          'transactions.receiverid = agententry.agentid '
                          'WHERE spec LIKE "%Reactor%" '
                          'GROUP BY time').fetchall()

    return get_timeseries(fuel, duration, .001, 'TRUE')


def u_util_calc(cursor):
    """ Returns fuel utilization factor of fuel cycle

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor

    Returns
    -------
    u_util_timeseries: numpy array
        Timeseries of Uranium utilization factor
    Prints simulation average Uranium Utilization
    """
    # timeseries of natural uranium
    u_supply_timeseries = np.array(nat_u_timeseries(cursor))

    # timeseries of fuel into reactors
    fuel_timeseries = np.array(fuel_into_reactors(cursor))

    # timeseries of Uranium utilization
    u_util_timeseries = np.nan_to_num(fuel_timeseries / u_supply_timeseries)
    # print the simulation average uranium utilization
    print('The Simulation Average Uranium Utilization is:')
    print(sum(u_util_timeseries) / len(u_util_timeseries))

    # return dictionary of u_util_timeseries
    return u_util_timeseries


def where_comm(cursor, commodity, prototypes):
    """ Returns dict of where a commodity is from

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor
    commodity: str
        name of commodity
    prototypes: list
        list of prototypes that provides commodity

    Returns
    -------
    trade_dict: dictioary
        dictionary with key: prototype name,
        value: timeseries of commodity sent from prototypes
    """
    init_year, init_month, duration, timestep = get_sim_time_duration(cursor)
    query = ('SELECT time, sum(quantity) FROM transactions '
             'INNER JOIN resources ON resources.resourceid = '
             'transactions.resourceid WHERE commodity = ' +
             str(commodity) + ' AND senderid '
             '= 9999 GROUP BY time')
    trade_dict = collections.OrderedDict()
    for agent in prototypes:
        agent_id = get_prototype_id(cursor, agent)
        from_agent = cursor.execute(query.replace(
            '9999', ' OR senderid = '.join(agent_id))).fetchall()
        trade_dict[agent] = get_timeseries(from_agent, duration, .001, 'TRUE')

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
        dictionary with key: isotope,
        value: mass timeseries of each unique isotope
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
        dictionary with key: government,
        value: timesereies capacity
    num_dict: dictionary
        dictionary with key: government,
        value: timesereis number of reactors
    """
    power_dict = collections.OrderedDict()
    num_dict = collections.OrderedDict()
    for gov in governments:
        capacity = []
        num_reactors = []
        cap = 0
        count = 0
        for t in timestep:
            for enter in entry:
                entertime = enter[3]
                parentgov = enter[2]
                gov_agentid = gov[1]
                power_cap = enter[0]
                if entertime == t and parentgov == gov_agentid:
                    cap += power_cap / 1000
                    count += 1
            for dec in exit_step:
                exittime = dec[3]
                parentgov = dec[2]
                gov_agentid = gov[1]
                power_cap = dec[0]
                if exittime == t and parentgov == gov_agentid:
                    cap -= power_cap / 1000
                    count -= 1
            capacity.append(cap)
            num_reactors.append(count)
        power_dict[gov[0]] = np.asarray(capacity)
        num_dict[gov[0]] = np.asarray(num_reactors)

    return power_dict, num_dict


"""PLOTTER"""


def multi_line_plot(dictionary, timestep,
                    xlabel, ylabel, title,
                    outputname, init_year):
    """ Creates a multi-line plot of timestep vs dictionary

    Parameters
    ----------
    dictionary: dictionary
        dictionary with value: list of timestep progressions
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

        plt.plot(init_year + (timestep / 12),
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
            plot = plt.bar(left=init_year + (timestep / 12),
                           height=dictionary[key],
                           width=0.1,
                           color=cm.viridis(
                1. * color_index / len(dictionary)),
                edgecolor='none',
                label=label)
            prev = dictionary[key]
            top_index = False
            plot_list.append(plot)

        # All curves except the first have a 'bottom'
        # defined by the previous curve
        else:
            plot = plt.bar(left=init_year + (timestep / 12),
                           height=dictionary[key],
                           width=0.1,
                           color=cm.viridis(
                1. * color_index / len(dictionary)),
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
    plt.legend(loc=(1.0, 0))
    plt.grid(True)
    plt.savefig(outputname + '.png', format='png', bbox_inches='tight')
    plt.close()


def plot_power(cursor):
    """ Gets capacity vs time for every country
        in stacked bar chart.

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor

    Returns
    -------
    """
    init_year, init_month, duration, timestep = get_sim_time_duration(cursor)
    power_dict, num_dict = get_power_dict(cursor)
    stacked_bar_chart(power_dict, timestep,
                      'Years', 'Net_Capacity [GWe]',
                      'Net Capacity vs Time', 'power_plot', init_year)

    stacked_bar_chart(num_dict, timestep,
                      'Years', 'Number of Reactors',
                      'Number of Reactors vs Time',
                      'number_plot', init_year)


def plot_in_out_flux(cursor, facility, influx_bool, title, outputname):
    """plots timeseries outflux from facility name in kg.

    Parameters
    ----------
    cursor: sqlite cursor
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
    agent_ids = get_agent_ids(cursor, facility)
    if influx_bool is True:
        resources = cursor.execute(exec_string(agent_ids,
                                               'transactions.receiverId',
                                               'time, sum(quantity), '
                                               'qualid') +
                                   ' GROUP BY time, qualid').fetchall()
    else:
        resources = cursor.execute(exec_string(agent_ids,
                                               'transactions.senderId',
                                               'time, sum(quantity), '
                                               'qualid') +
                                   ' GROUP BY time, qualid').fetchall()

    compositions = cursor.execute('SELECT qualid, nucid, massfrac '
                                  'FROM compositions').fetchall()

    init_year, init_month, duration, timestep = get_sim_time_duration(cursor)
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


if __name__ == "__main__":
    file = sys.argv[1]
    con = lite.connect(file)
    with con:
        cur = con.cursor()
        init_year, init_month, duration, timestep = get_sim_time_duration(cur)

# Europe History Case Only
        tailings = commodity_in_out_facility(
            cur, 'enrichment', ['tailings'], True)
        stacked_bar_chart(tailings, timestep,
                          'Year', 'Mass [MTHM]',
                          'Tailings vs Time',
                          'tailings',
                          init_year)
        # uox_pu = commodity_from_facility(cur, 'separations', ['uox_Pu'])
        # stacked_bar_chart(uox_pu, timestep,
        #                  'Year', 'Mass [MTHM]',
        #                  'Pu output (UOX) vs Time',
        #                  'tailings',
        #                  init_year)

        # mox_pu = commodity_from_facility(cur, 'separations', ['mox_Pu'])
        # stacked_bar_chart(mox_pu, timestep,
        #                  'Year', 'Mass [MTHM]',
        #                  'Pu output (MOX) vs Time',
        #                  'tailings',
        #                  init_year)
        # stacked_bar_chart(uox_pu, timestep,
        #                  'Year', 'Mass [MTHM]',
        #                  'Pu output (UOX) vs Time',
        #                  'tailings',
        #                  init_year)

        # mox_pu = commodity_from_facility(cur, 'separations', ['mox_Pu'])
        # stacked_bar_chart(mox_pu, timestep,
        #                  'Year', 'Mass [MTHM]',
        #                  'Pu output (MOX) vs Time',
        #                  'tailings',
        #                  init_year)

        plot_power(cur)
        fuel_dict = fuel_usage_timeseries(cur, ['uox', 'mox'])
        stacked_bar_chart(fuel_dict, timestep,
                          'Years', 'Mass[MTHM]',
                          'Total Fuel Mass vs Time',
                          'total_fuel',
                          init_year)

        dictionary = {}
        dictionary['uranium_utilization'] = u_util_calc(cur)
        stacked_bar_chart(dictionary, timestep,
                          'Years', 'U Utilization Factor',
                          'U Utilization vs Time',
                          'u_util', init_year)
"""
combined case

        # rep_dict = get_trade_dict(cur, 'separations', 'reactor', False, True)
        # stacked_bar_chart(rep_dict, timestep,
        #                  'Year', 'Mass [MTHM]',
        #                  'reprocessing product vs time',
        #                  'rep_product', init_year)
        # tailings = commodity_in_out_facility(cur, 'enrichment',
                                               ['tailings'], True)
        # stacked_bar_chart(tailings, timestep,
        #                  'Year', 'Mass [MTHM]',
        #                  'Tailings vs Time',
        #                  'tailings',
        #                  init_year)
        fuel_dict = where_comm(cur, 'mox', ['uox_mixer', 'mox_mixer'])
        stacked_bar_chart(fuel_dict, timestep,
                          'Years', 'Mass[MTHM]',
                          'Total Fuel Mass vs Time',
                          'total_fuel',
                          init_year)
        demand = collections.OrderedDict()
        demand['pu_from_legacy'] = [i * .09 for i in fuel_dict['uox_mixer']]
        demand['pu_from_spent_mox'] = [i * .09 for i in fuel_dict['mox_mixer']]
        total_mox = ([x + y for x, y in zip(fuel_dict['uox_mixer'],
                                            fuel_dict['mox_mixer'])])
        demand['pu_total'] = [i *.09 for i in total_mox]
        demand['tailings'] = [i * .91 for i in total_mox]

        multi_line_plot(demand, timestep,
                        'Years', 'Mass[MTHM]',
                        'Total Demand vs Time',
                        'demand',
                        init_year)

        reprocessing_waste = get_trade_dict(cur, 'separations',
                                            'sink', False, False)
        stacked_bar_chart(reprocessing_waste, timestep,
                          'Year', 'Mass [MTHM]',
                          'reprocessing waste vs time',
                          'repro_waste',
                          init_year)

        plot_power(cur)
        #dictionary = {}
        #dictionary['uranium_utilization'] = u_util_calc(cur)
        #stacked_bar_chart(dictionary, timestep,
        #                  'Years', 'U Utilization Factor',
        #                  'U Utilization vs Time',
        #                  'u_util', init_year)

"""
"""
        init_year, init_month, duration, timestep = get_sim_time_duration(cur)

        # waste_dict = total_waste_timeseries(cur)
        # multi_line_plot(waste_dict, timestep,
        #                'Years', 'Mass[MTHM]',
        #                'Total Waste Mass vs Time',
        #                'total_Waste',
        #                init_year)

        fuel_dict = fuel_usage_timeseries(cur, ['uox', 'mox'])

        stacked_bar_chart(fuel_dict, timestep,
                          'Years', 'Mass[MTHM]',
                          'Total Fuel Mass vs Time',
                          'total_fuel',
                          init_year)

        tailings = commodity_from_facility(cur, 'enrichment', ['tailings'])
        stacked_bar_chart(tailings, timestep,
                          'Year', 'Mass [MTHM]',
                          'Tailings vs Time',
                          'tailings',
                          init_year)
"""
