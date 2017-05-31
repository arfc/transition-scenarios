import sqlite3 as lite
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import collections



if len(sys.argv) < 2:
    print('Usage: python analysis.py [cylus_output_file]')


def snf(cursor):
    """prints total snf and isotope mass

    Parameters
    ----------
    cursor: cursor
        cursor for sqlite3

    Returns
    -------
    array
        inventory of individual nuclides
        in format nuclide = mass [kg]
    """

    cur = cursor

    sink_id = get_agent_ids(cur, 'sink')

    # get resources that ended up in sink.
    resources = cur.execute(exec_string(sink_id,
                                        'transactions.receiverId',
                                        'qualid')).fetchall()

    # get list of sum(quantity) and qualid for snf
    snf_inventory = cur.execute(exec_string(sink_id,
                                            'transactions.receiverId',
                                            'sum(quantity), qualid')
                                + ' group by qualid').fetchall()

    waste_id = get_waste_id(resources)
    return isotope_calc(waste_id, snf_inventory, cur)


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
        name of facility type

    Returns
    -------

    sink_id: list
        list of all the sink agentId values.
    """

    cur = cursor
    agent_id = []
    agent = cur.execute("select * from agententry where spec like '%"
                        + facility + "%'").fetchall()

    for ag in agent:
        agent_id.append(ag[1])
    return agent_id


def get_waste_id(resource_list):

    """ Gets waste id from a resource list

    Parameters
    ---------
    resource_list: list
        list fetched from the resource table.

    Returns
    -------
    waste_id: list
        list of qualId for waste
    """

    wasteid = []

    for res in resource_list:

        wasteid.append(res[0])

    return set(wasteid)


def exec_string(list, search, whatwant):
    """ Generates sqlite query command to select things and
        inner join between resources and transactions.

    Parameters
    ---------

    list: list
        list of criteria that generates command
    search: str
        where [search]
        criteria for your search
    whatwant: str
        select [whatwant]
        column (set of values) you want out.

    Returns
    -------
    str
        sqlite query command.
    """

    exec_str = ('select ' + whatwant + ' from resources inner join transactions\
                on transactions.resourceid = resources.resourceid where '
                + str(search) + ' = ' + str(list[0]))

    for ar in list[1:]:
        exec_str += ' and ' + str(ar)

    return exec_str


def get_sum(list, column_index):
    """ Returns sum of a column in an list

    Parameters:
    ---------
    list: list
        list that contains a column with numbers
    column_index: int
        index for the column to be summed

    Returns
    -------
    int
        summation of all the values in the array column
    """
    sum = 0
    for ar in list:
        sum += ar[column_index]

    return sum


def isotope_calc(wasteid_array, snf_inventory, cursor):
    """ Calculates isotope mass using mass fraction in compositions table.

        Fetches all compositions from compositions table.
        Compositions table has the following format:
            SimId / QualId / NucId / MassFrac
        Then sees if the qualid matches, and if it does, multiplies
        the mass fraction by the snf_inventory.

    Parameters
    ---------
    wasteid_list: list
        list of qualid of wastes
    snf_inventory: float
        total mass of snf [kg]
    cursor: cursor
        cursor for sqlite3

    Returns
    -------
    nuclide_inven: list
        inventory of individual nuclides.
    """

    # Get compositions of different waste
    # SimId / QualId / NucId / MassFrac
    cur = cursor
    comps = cur.execute('select * from compositions').fetchall()
    total_snf_mass = get_sum(snf_inventory, 0)

    nuclide_inven = 'total snf inventory = ' + str(total_snf_mass) + 'kg \n'
    nuclides = []
    mass_of_nuclides = []
    # if the 'qualid's match,
    # the nuclide quantity and calculated and displayed.
    for comp in comps:
        for num in snf_inventory:
            inv_qualid = num[1]
            comp_qualid = comp[1]
            if inv_qualid == comp_qualid:
                comp_tot_mass = num[0]
                mass_frac = comp[3]
                nuclide_quantity = comp_tot_mass * mass_frac
                nucid = comp[2]
                nuclide_name = nucid
                nuclides.append(nuclide_name)
                mass_of_nuclides.append(nuclide_quantity)
    return sum_nuclide_to_dict(nuclides, mass_of_nuclides)


def sum_nuclide_to_dict(nuclides, nuclides_mass):
    """takes a nuclide set and returns a dictionary with the masses of each nuclide

    Parameters
    ----------
    nuclides: list
        list of nuclides in the waste
    nuclides_mass: list
        list of nuclides' mass

    Returns
    -------
    dict
        dictionary of nuclide name and mass
    """

    nuclide_set = set(nuclides)
    mass_dict = collections.OrderedDict({})

    for nuclide in nuclide_set:
        temp_nuclide_sum = 0
        indeces =[i for i, x in enumerate(nuclides) if x == nuclide]
        for index in indeces:
            temp_nuclide_sum += nuclides_mass[index]
        mass_dict[str(nuclide)] = temp_nuclide_sum

    print(mass_dict)
    return mass_dict


def get_sim_time_duration(cursor):
    """ Returns simulation time and duration of the simulation

    Parameters
    ----------
    cursor: sqlite cursor

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
    cur = cursor

    info = cur.execute('SELECT initialyear, initialmonth,'
                       + ' duration FROM info').fetchone()
    init_year = info[0]
    init_month = info[1]
    duration = info[2]
    timestep = np.linspace(0, info[2]-1, num=info[2])

    return init_year, init_month, duration, timestep


def isotope_mass_time_list(resources, compositions):
    """Creates an list with isotope name, mass, and time

    Parameters
    ----------
    resources: list
        resource data from the resources table
    compositions: list
        composition data from the compositions table

    Returns
    -------
    list
        isotope name list
    list
        isotope mass list
    list
        isotope transaction time list

    """

    temp_isotope = []
    temp_mass = []
    time_list = []

    for res in resources:
        for com in compositions:
            res_qualid = res[2]
            comp_qualid = com[1]
            if res_qualid == comp_qualid:
                nucid = com[2]
                mass_frac = com[3]
                mass_waste = res[0]
                res_time = res[1]
                temp_isotope.append(nucid)
                temp_mass.append(mass_frac*mass_waste)
                time_list.append(res_time)

    return temp_isotope, temp_mass, time_list


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

    cur = cursor
    agent_ids = get_agent_ids(cur, facility)
    if influx_bool is True:
        resources = cur.execute(exec_string(agent_ids,
                                            'transactions.receiverId',
                                            'sum(quantity), time, qualid')
                                + ' GROUP BY time, qualid').fetchall()
    else:
        resources = cur.execute(exec_string(agent_ids,
                                            'transactions.senderId',
                                            'sum(quantity), time, qualid')
                                + ' GROUP BY time, qualid').fetchall()
    compositions = cur.execute('SELECT * FROM compositions').fetchall()
    init_year, init_month, duration, timestep = get_sim_time_duration(cur)
    isotope, mass, time_list = isotope_mass_time_list(resources, compositions)

    waste_dict = get_waste_dict(isotope, mass, time_list, duration)

    if influx_bool is False:
        stacked_bar_chart(waste_dict, timestep,
                          'Years', 'Mass [kg]',
                          title, outputname, init_year)
    else:
        multi_line_plot(waste_dict, timestep,
                        'Years', 'Mass [kg]',
                        title, outputname, init_year)


def get_from_facility(cursor, facility, duration, resources):
    """ Returns timeseries list of quantity out of facility type

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor
    facility: str
        name of facility type
    duration: int
        duration of simulation
    resrources: list
        list of lists, of quantity, senderid and time

    Returns
    -------
    list
    timeseries list of mass outflux from facility type
    """

    quantity = 0 
    timeseries = []
    agentid = cursor.execute('SELECT agentid FROM agententry WHERE spec \
                             LIKE "%' + facility + '%"').fetchall()
    agentid = np.array(agentid)
    for i in range(0, duration):
        for row in resources:
            transaction_time = row[2]
            senderid = row[1]
            mass = row[0]
            if transaction_time == i and senderid in agentid:
                quantity += mass
        timeseries.append(quantity/1000)

    return timeseries


def total_waste_timeseries(cursor):
    """Plots a stacked bar chart of the total waste mass vs time

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor

    Returns
    -------
    null
    stacked bar chart of waste mass vs time
    """

    cur = cursor
    agent_ids = get_agent_ids(cur, 'sink')
    resources = cur.execute(exec_string(agent_ids,
                                        'transactions.receiverId',
                                        'sum(quantity), senderid, time')
                            + ' GROUP BY time, senderid').fetchall()

    init_year, init_month, duration, timestep = get_sim_time_duration(cur)
    waste_dict = collections.OrderedDict({})

    waste_dict['Reactor'] = get_from_facility(cur,'Reactor', duration, resources)
    waste_dict['Separations'] = get_from_facility(cur,'Separations', duration, resources)
    waste_dict['Tails'] = get_from_facility(cur, 'Enrichment', duration, resources)

    return waste_dict

def get_stockpile(cursor, facility):
    """ get stockpile timeseries in a fuel facility

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor
    facility: str
        name of facility

    Returns
    -------
    null
    line plot of stockpile inventory
    """

    cur = cursor
    pile_dict = collections.OrderedDict({})
    agentid = get_agent_ids(cur, facility)
    query = exec_string(agentid, 'agentid', 'timecreated, quantity, qualid')
    query = query.replace('transactions', 'agentstateinventories')
    stockpile = cur.execute(query).fetchall()
    init_year, init_month, duration, timestep = get_sim_time_duration(cur)
    stock_timeseries = get_timeseries(stockpile, duration, .001)
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
    dictionary of swu timeseries
    """

    cur = cursor
    swu_dict = collections.OrderedDict({})
    agentid = get_agent_ids(cur, 'Enrichment')
    init_year, init_month, duration, timestep = get_sim_time_duration(cur)
    facility_num = 1
    for num in agentid:
        swu_data = cur.execute('SELECT time, value FROM timeseriesenrichmentswu \
                               WHERE agentid = ' + str(num)).fetchall()
        swu_timeseries = get_timeseries(swu_data, duration, 1)
        swu_dict['Enrichment' + str(facility_num)] = swu_timeseries
        facility_num += 1

    return swu_dict


def get_timeseries(list, duration, multiplyby):
    """ creates a returns a timeseries list of a given data

    Parameters
    ----------
    list: list
        list of data to be created into timeseries
        list[0] = time
        list[1] = value, quantity
    duration: int
        duration of the simulation
    multiplyby: int
        integer to multiply the value in the list by 

    Returns
    -------
    timeseries list of data
    """

    value = 0
    value_timeseries = []
    array = np.array(list)

    for i in range(0, duration):
    	bool_indx = (array[:,0] == i )
    	value += sum(array[bool_indx])
    	value_timeseries.append(value*multiplyby)

    return value_timeseries



def final_stockpile(cursor, facility):
    """ get final stockpile in a fuel facility

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor
    facility: str
        name of facility

    ReturnsW
    -------
    MTHM value of stockpile
    """
    cur = cursor
    stock_dict = collections.OrderedDict({})
    agentid = get_agent_ids(cur, facility)
    for agent in agentid:
        count = 1
        name = cur.execute('SELECT prototype FROM agententry WHERE agentid = ' + str(agent)).fetchone()
        print('The Stockpile in ' + name[0] + ' : ')
        stockpile = cur.execute("""SELECT sum(quantity), inventoryname, qualid
                                 FROM agentstateinventories
                                 INNER JOIN resources
                                 ON resources.resourceid = agentstateinventories.resourceid
                                 WHERE agentstateinventories.agentid 
                                 = """ + str(agent) + """ GROUP BY
                                 inventoryname""").fetchall()
        for stream in stockpile:
            masses = cur.execute('SELECT * FROM compositions WHERE qualid = ' + str(stream[2])).fetchall()
            print('Stream ' + str(count) + ' Total = ' + str(stream[0]) + ' kg')
            for isotope in masses:
                print(nucname.name(isotope[2]) + ' = ' + str(isotope[3]*stream[0]) + ' kg')
            print('\n')
            count +=1 
        print('\n')
    print('\n')


def fuel_usage_timeseries(cursor, fuel_list):
    """ Calculates total fuel usage over time

    Parameters
    ----------
    cursor: sqlite cursor
        sqlite cursor
    fuel_list: list
        list of fuel commodity names (eg. uox, mox)

    Returns
    -------
    dict
        dictionary of different fuels used timeseries
    """

    cur = cursor
    fuel_dict = collections.OrderedDict({})
    for fuel in fuel_list:
        temp_list = ['"' + fuel + '"']
        fuel_quantity = cur.execute(exec_string(temp_list, 'commodity',
                                    'sum(quantity), time')
                                    + ' GROUP BY time').fetchall()
        init_year, init_month, duration, timestep = get_sim_time_duration(cur)
        total_sum = 0
        quantity_timeseries = []
        for i in range(0, duration):
            for row in fuel_quantity:
                transaction_time = row[1]
                if transaction_time == i:
                    quantity = row[0]
                    total_sum += quantity
            quantity_timeseries.append(total_sum)
        fuel_dict[fuel] = quantity_timeseries

    return fuel_dict


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
    dict
        dictionary of mass time series of each unique isotope
    """

    waste_dict = collections.OrderedDict({})
    isotope_set = set(isotope_list)

    for iso in isotope_set:
        mass = 0
        time_mass = []
        # at each timestep,
        for i in range(0, duration):
            # for each element in database,
            for x in range(0, len(isotope_list)):
                if i == time_list[x] and isotope_list[x] == iso:
                    mass += mass_list[x]
            time_mass.append(mass)
        waste_dict[iso] = time_mass

    return waste_dict


def power_timeseries(cursor):
    """Returns dictionary of power timeseries

    Parameters:
    cursor: sqlite cursor
        sqlite cursor

    Returns:
    Dictionary of power timeseries
    """

    cur = cursor
    power_timeseries_dict = collections.OrderedDict({})
    timeseriespower = np.array(cur.execute('SELECT sum(value) FROM\
                                   timeseriespower GROUP BY time').fetchall())
    power_timeseries_dict['powertimeseries'] = (timeseriespower[:,0])

    return power_timeseries_dict




def capacity_calc(governments, timestep, entry, exit_step):

    """Adds and subtracts capacity over time for plotting

    Parameters
    ---------
    governments: list
        list of governments (countries)
    timestep: list
        list of timestep from 0 to simulation time
    entry: list
        power_cap, agentid, parentid, entertime
        of all entered reactors

    exit_step: list
        power_cap, agentid, parenitd, exittime
        of all decommissioned reactors

    Returns
    -------
    tuple
        (power_dict, num_dict) which holds timeseries
        of capacity and number of reactors
        with country_government as key
    """

    power_dict = collections.OrderedDict({})
    num_dict = collections.OrderedDict({})

    for gov in governments:
        capacity = []
        num_reactors = []
        cap = 0
        count = 0
        gov_name = gov[0]
        print(gov)
        for t in timestep:
            for enter in entry:
                entertime = enter[3]
                parentgov = enter[2]
                gov_agentid = gov[1]
                power_cap = enter[0]
                if entertime == t and parentgov == gov_agentid:
                    print(power_cap)
                    cap += power_cap
                    count += 1
            for dec in exit_step:
                exittime = dec[3]
                parentgov = dec[2]
                gov_agentid = gov[1]
                power_cap = dec[0]
                if exittime == t and parentgov == gov_agentid:
                    cap -= power_cap
                    count -= 1
            capacity.append(cap)
            num_reactors.append(count)

        power_dict[gov[0]] = np.asarray(capacity)
        num_dict[gov[0]] = np.asarray(num_reactors)

    return power_dict, num_dict


def multi_line_plot(dictionary, timestep,
                    xlabel, ylabel, title,
                    outputname, init_year):
    """ Creates a multi-line plot of timestep vs dictionary

    Parameters
    ----------
    dictionary: dictionary
        dictionary with list of timestep progressions
    timestep: int
        timestep of simulation (linspace)
    xlabel: string
        xlabel of plot
    ylabel: string
        ylabel of plot
    title: string
        title of plot
    init_year: int
        initial year of simulation
    Returns
    -------
    stores a plot of dict data on path `outputname`
    """

    # set different colors for each bar
    color_index = 0
    prev = ''
    plot_list = []
    # for every country, create bar chart with different color
    for key in dictionary:
        # label is the name of the nuclide (converted from ZZAAA0000 format)
        if isinstance(key, str) is True:
            label = key.replace('_government', '')
        else:
            label = str(key)
        plt.plot(init_year + (timestep/12),
                 dictionary[key],
                 label=label)
        color_index += 1
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
        holds time series data
    timestep: list
        list of timestep (x axis)
    xlabel: string
        xlabel of plot
    ylabel: string
        ylabel of plot
    title: string
        title of plot
    init_year: int
        simulation start year

    Returns
    -------

    """

    # set different colors for each bar
    color_index = 0
    top_index = True
    prev = ''
    plot_list = []
    # for every country, create bar chart with different color
    for key in dictionary:
        if isinstance(key, str) is True:
            label = key.replace('_government', '')
        else:
            label = str(nucname.name(key))
        # very first country does not have a 'bottom' argument
        if "Sink" in key:
            print("Ignore Sink Institution")
        elif top_index is True:
            plot = plt.bar(left=init_year + (timestep/12),
                           height=dictionary[key],
                           width=0.1,
                           color=cm.viridis(1.*color_index/len(dictionary)),
                           edgecolor='none',
                           label=label)
            prev = dictionary[key]
            top_index = False
            plot_list.append(plot)

        # All curves except the first have a 'bottom'
        # defined by the previous curve
        else:
            plot = plt.bar(left=init_year + (timestep/12),
                           height=dictionary[key],
                           width=0.1,
                           color=cm.viridis(1.*color_index/len(dictionary)),
                           edgecolor='none',
                           bottom=prev,
                           label=label)
            prev = np.add(prev, dictionary[key])
            plot_list.append(plot)

        
        color_index += 1

    # plot
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
    cursor: cursor
        cursor for sqlite3

    Returns
    -------
    stacked bar chart of net capacity vs time

    """

    cur = cursor
    init_year, init_month, duration, timestep = get_sim_time_duration(cur)
    powercap = []
    reactor_num = []
    countries = []
    cur = cursor
    # get power cap values
    governments = cur.execute('SELECT prototype, agentid FROM agententry\
                              WHERE kind = "Inst"').fetchall()

    entry = cur.execute('SELECT max(value), timeseriespower.agentid, parentid, entertime\
                         FROM agententry INNER JOIN timeseriespower\
                         ON agententry.agentid = timeseriespower.agentid\
                         GROUP BY timeseriespower.agentid').fetchall()

    exit_step = cur.execute('SELECT max(value), timeseriespower.agentid, parentid, exittime\
                        FROM agentexit INNER JOIN\
                        timeseriespower\
                        ON agentexit.agentid =\
                        timeseriespower.agentid\
                        INNER JOIN agententry\
                        ON agentexit.agentid = agententry.agentid\
                        group by timeseriespower.agentid').fetchall()
    power_dict, num_dict = capacity_calc(governments, timestep,
                                         entry, exit_step)

    stacked_bar_chart(power_dict, timestep,
                      'Time', 'net_capacity',
                      'Net Capacity vs Time', 'power_plot', init_year)

    stacked_bar_chart(num_dict, timestep,
                      'Time', 'num_reactors',
                      'Number of Reactors vs Time',
                      'number_plot', init_year)

if __name__ == "__main__":
    file = sys.argv[1]
    con = lite.connect(file)
    with con:
        cur = con.cursor()
        init_year, init_month, duration, timestep = get_sim_time_duration(cur)
        """
        print(snf(cur))
        power_timeseries_dict = power_timeseries(cur)
        stacked_bar_chart(power_timeseries_dict, np.delete(timestep,0,0),
                          'Years', 'Power [MWe]',
                          'Total Power Active Cap vs Time',
                          'powertimeseries',
                          init_year)
        plot_power(cur)
        plot_in_out_flux(cur, 'sink', True, 'isotope vs time', 'sink')
        plot_in_out_flux(cur, 'source', False, 'source vs time', 'source')
        """
        
        """
            waste_dict ['Reactor'] = uox_waste
            waste_dict ['Enrichment'] = tailing
            waste_dict ['Separations'] = reprocess waste (FP, MA)
            pile_dict ['Mixer'] = tailing
            pile_dict2 ['Separation'] = reprocessed U
        
        waste_dict = total_waste_timeseries(cur)
        multi_line_plot(waste_dict, timestep,
                        'Years', 'Mass[MTHM]',
                        'Total Waste Mass vs Time',
                        'total_Waste',
                        init_year)

        fuel_dict = fuel_usage_timeseries(cur, ['uox', 'mox','fr_fuel'])
        stacked_bar_chart(fuel_dict, timestep,
                          'Years', 'Mass[MTHM]',
                          'Total Fuel Mass vs Time',
                          'total_fuel',
                          init_year)

"""
        swu_dict = get_swu_dict(cur)
        multi_line_plot(swu_dict, timestep,
                        'Years', 'SWU',
                        'Total SWU vs Time',
                        'SWU', init_year)
"""
        try:
            final_stockpile(cur, 'Mixer')
            final_stockpile(cur, 'Separations')

            pile_dict = get_stockpile(cur, 'Mixer')
            multi_line_plot(pile_dict, timestep,
                            'Years', 'Mass[MTHM]',
                            'Tailings left over in Mixer vs Time',
                            'Total_Stockpile', init_year)
            pile_dict2 = get_stockpile(cur, 'Separations')
            multi_line_plot(pile_dict2, timestep,
                            'Years', 'Mass[MTHM]',
                            'Total Stockpile of ReprU vs Time',
                            'Total_Stockpile', init_year)
            tail_dict = collections.OrderedDict({})
            tail_dict['tailing'] = [x + y for x, y in zip(waste_dict['Tails'],
                                    pile_dict['Mixer'])]
            multi_line_plot(tail_dict, timestep,
                            'Years', 'Mass[MTHM]',
                            'Total Tailing vs Time', 'Total_tailings',
                            init_year)
        except:
            print('Seems like it is once through')
"""