import sqlite3 as lite
import sys
from pyne import nucname
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import collections
import pylab


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


def get_waste_id(resource_array):
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


    for res in resource_array:
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
    nuclides: array
        array of nuclides in the waste
    nuclides_mass: array
        array of nuclides' mass

    Returns
    -------
    dict
        dictionary of nuclide name and mass
    """

    nuclide_set = set(nuclides)
    mass_dict = collections.OrderedDict({})

    for nuclide in nuclide_set:
        temp_nuclide_sum = 0
        for i in range(len(nuclides)):
            if nuclides[i] == nuclide:
                temp_nuclide_sum += nuclides_mass[i]
        nuclide_name = str(nucname.name(nuclide))
        mass_dict[nuclide_name] = temp_nuclide_sum

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
    timestep = np.linspace(1, info[2], num=info[2])
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
        print(iso)
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
        for t in timestep:
            for enter in entry:
                entertime = enter[3]
                parentgov = enter[2]
                gov_name = gov[1]
                power_cap = enter[0]
                if entertime == t and parentgov == gov_name:
                    cap += power_cap
                    count += 1
            for dec in exit_step:
                exittime = dec[3]
                parentgov = dec[2]
                gov_name = gov[1]
                power_cap = dec[0]
                if exittime == t and parentgov == gov_name:
                    cap -= power_cap
                    count -= 1
            capacity.append(cap)
            num_reactors.append(count)

        power_dict[gov[0]] = np.asarray(capacity)
        num_dict[gov[0]] = np.asarray(num_reactors)

    return power_dict, num_dict


def years_from_start(cursor, timestep):
    """
    Returns a fractional year from the start
    of the simulation (e.g. 1950.5 for June 1950)
    based on the timestep

    Parameters
    ----------
    cursor: sqlite cursor
        cursor to the sqlite file
    timesteps: array
        array of timesteps to convert into year

    Returns
    -------
    float
        the fractional year, representing the timestep given
    """
    cur = cursor
    startdate = cur.execute('SELECT initialyear,'
                            + ' initialmonth FROM info').fetchall()
    startyear = startdate[0][0]
    startmonth = startdate[0][1]

    return float(startyear) + (timestep + startmonth)/12.0


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
    stores a semilogy plot of dict data on path `outputname`
    """

    # set different colors for each bar
    color_index = 0
    prev = ''
    plot_list = []
    # for every country, create bar chart with different color
    for key in dictionary:
        # label is the name of the nuclide (converted from ZZAAA0000 format)
        label = str(nucname.name(key))
        plt.semilogy(left=init_year + (timestep/12),
                     height=dictionary[key],
                     label=label)
        color_index += 1
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.legend(loc=(1.0, 0),
                   prop={'size':10})
        plt.grid(True)
        plt.savefig(label + '_' + outputname,
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
        if top_index is True:
            plot = plt.bar(left=init_year + (timestep/12),
                           height=dictionary[key],
                           width=0.5,
                           color=cm.viridis(1.*color_index/len(dictionary)),
                           edgecolor='none',
                           label=label)
            prev = dictionary[key]
            top_index = False
        # All curves except the first have a 'bottom'
        # defined by the previous curve
        else:
            plot = plt.bar(left=init_year + (timestep/12),
                           height=dictionary[key],
                           width=0.5,
                           color=cm.viridis(1.*color_index/len(dictionary)),
                           edgecolor='none',
                           bottom=prev,
                           label=label)
            prev += dictionary[key]

        plot_array.append(plot)
        plot_list.append(plot)
        color_index += 1

    # plot
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.legend(loc=(1.0, 0))
    plt.grid(True)
    plt.savefig(outputname, format='png', bbox_inches='tight')
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
                              WHERE spec LIKE "%Inst%"').fetchall()

    entry = cur.execute('SELECT power_cap, agententry.agentid, parentid, entertime\
                        FROM agententry INNER JOIN\
                        agentstate_cycamore_reactorinfo\
                        ON agententry.agentid =\
                        agentstate_cycamore_reactorinfo.agentid\
                        group by agententry.agentid').fetchall()

    exit_step = cur.execute('SELECT power_cap, agentexit.agentid, parentid, exittime\
                        FROM agentexit INNER JOIN\
                        agentstate_cycamore_reactorinfo\
                        ON agentexit.agentid =\
                        agentstate_cycamore_reactorinfo.agentid\
                        INNER JOIN agententry\
                        ON agentexit.agentid = agententry.agentid').fetchall()

    power_dict, num_dict = capacity_calc(governments, timestep,
                                         entry, exit_step)

    years = years_from_start(cur, timestep)
    stacked_bar_chart(power_dict, years,
                      'Time', 'net_capacity',
                      'Net Capacity vs Time', 'power_plot.png', init_year)
    plt.figure()
    stacked_bar_chart(num_dict, years,
                      'Time', 'num_reactors',
                      'Number of Reactors vs Time',
                      'number_plot.png', init_year)

if __name__ == "__main__":
    file = sys.argv[1]
    con = lite.connect(file)
    with con:
        cur = con.cursor()
        print(snf(cur))
        plot_power(cur)
        plot_in_out_flux(cur, 'source', False, 'source vs time', 'source')
        plot_in_out_flux(cur, 'sink', True, 'isotope vs time', 'sink')
