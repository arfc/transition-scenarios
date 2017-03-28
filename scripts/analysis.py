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


def snf(filename, cursor):
    """prints total snf and isotope mass

    Parameters
    ----------
    filename: str
        cyclus output file to be analyzed.
    cursor: cursor
        cursor for sqlite3

    Returns
    -------
    array
        inventory of individual nuclides
        in format nuclide = mass [kg]
    """

    cur = cursor

    sink_id = get_sink_agent_ids(cur)

    # get resources that ended up in sink.
    resources = cur.execute(exec_string(sink_id,
                                        'transactions.receiverId',
                                        'qualid')).fetchall()
    # get array of sum(quantity) and qualid for snf
    snf_inventory = cur.execute(exec_string(sink_id,
                                            'transactions.receiverId',
                                            'sum(quantity), qualid')
                                            + ' group by qualid').fetchall()
    waste_id = get_waste_id(resources)
    return isotope_calc(waste_id, snf_inventory, cur)


def get_sink_agent_ids(cursor):
    """Gets all sink agentIds from Agententry table.

        agententry table has the following format:
            SimId / AgentId / Kind / Spec /
            Prototype / ParentID / Lifetime / EnterTime

    Parameters
    ----------
    cursor: cursor
        cursor for sqlite3

    Returns
    -------
    array
        array of all the sink agentId values.
    """

    cur = cursor
    sink_id = []
    agent = cur.execute("select * from agententry where spec like '%sink%'")

    for ag in agent:
        sink_id.append(ag[1])
    return sink_id


def get_waste_id(resource_array):
    """Gets waste id from a resource array

    Parameters
    ----------
    resource_array: array
        array from the resource table that has all the qualids
        for all resources that went to the sink.

    Returns
    -------
    waste_id: set
        set of qualId for waste
    """

    wasteid = []

    for res in resource_array:
        wasteid.append(res[0])

    return set(wasteid)


def exec_string(array, search, whatwant):
    """Generates sqlite query command to select things an
        inner join between resources and transactions.

    Parameters
    ---------
    array: array
        array of criteria for searching what the 'search' value should match
        (i.e. agentIds)
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
                + str(search) + ' = ' + str(array[0]))

    for ar in array[1:]:
        exec_str += ' or ' + str(ar)

    return exec_str


def get_sum(array, column_index):
    """Returns sum of a column in an array

    Parameters
    ---------
    array: array
        array that contains a column with numbers
    column_index: int
        index for the column to be summed

    Returns
    -------
    int
        summation of all the values in the array column
    """
    result = 0
    for ar in array:
        result += ar[column_index]

    return result


def isotope_calc(wasteid_array, snf_inventory, cursor):
    """Calculates isotope mass using mass fraction in compositions table.

        Fetches all compositions from compositions table.
        Compositions table has the following format:
            SimId / QualId / NucId / MassFrac
        Then sees if the qualid matches, and if it does, multiplies
        the mass fraction by the snf_inventory.

    Parameters
    ---------
    wasteid_array: array
        array of qualid of wastes
    snf_inventory: float
        total mass of snf [kg]
    cursor: cursor
        cursor for sqlite3

    Returns
    -------
    nuclide_inven: array
        array of individual nuclides.
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


def capacity_calc(governments, timestep, entry, exit_step):
    """Adds and subtracts capacity over time for plotting

    Parameters
    ---------
    governments: array
        array of governments (countries)
    timestep: array
        array of timestep from 0 to simulation time
    entry: array
        power_cap, agentid, parentid, entertime
        of all entered reactors
    exit_step: array
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


def stacked_bar_chart(dictionary, timestep, xlabel, ylabel, title, outputname):
    """Creates stacked bar chart of timstep vs dictionary

    Parameters
    ----------
    dictionary: dictionary
        holds time series data
    timestep: array
        array of timestep (x axis)
    xlabel: string
        xlabel of plot
    ylabel: string
        ylabel of plot
    title: string
        title of plot

    Returns
    -------

    """

    # set different colors for each bar
    color_index = 0
    top_index = True
    prev = ''
    plot_array = []
    # for every country, create bar chart with different color
    for key in dictionary:
        if "government" in key:
            label = key.replace('_government', '')
        else:
            label = key
        # very first country does not have a 'bottom' argument
        if top_index is True:
            plot = plt.bar(left=timestep,
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
            plot = plt.bar(left=timestep,
                           height=dictionary[key],
                           width=0.5,
                           color=cm.viridis(1.*color_index/len(dictionary)),
                           edgecolor='none',
                           bottom=prev,
                           label=label)
            prev += dictionary[key]

        plot_array.append(plot)
        color_index += 1

    # plot
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.legend(loc=(1.0, 0))
    plt.grid(True)
    plt.savefig(outputname, format='png', bbox_inches='tight')


def plot_power(filename, cursor):
    """Gets capacity vs time for every country
        in stacked bar chart.

    Parameters
    ----------
    filename: file
        cyclus output file used
    cursor: cursor
        cursor for sqlite3

    Returns
    -------

    """
    cur = cursor
    sim_time = int(cur.execute('SELECT endtime FROM finish').fetchone()[0]) + 1
    timestep = np.linspace(0, sim_time, num=sim_time + 1)
    powercap = []
    reactor_num = []
    countries = []
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
                      'Net Capacity vs Time', 'power_plot.png')
    plt.figure()
    stacked_bar_chart(num_dict, years,
                      'Time', 'num_reactors',
                      'Number of Reactors vs Time', 'number_plot.png')


if __name__ == "__main__":
    file = sys.argv[1]
    con = lite.connect(file)

    with con:
        cur = con.cursor()
        print(snf(file, cur))
        plot_power(file, cur)
