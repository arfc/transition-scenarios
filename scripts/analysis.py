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
    Returns total snf and isotope mass.
    """

    cur = cursor

    sink_id = get_agent_ids(cur, 'sink')

    # get resources that ended up in sink.
    resources = cur.execute(exec_string(sink_id,
                                        'transactions.receiverId',
                                        '*')).fetchall()
    # get array of sum(quantity) and qualid for snf
    snf_inventory = cur.execute(exec_string(sink_id,
                                            'transactions.receiverId',
                                            'sum(quantity), qualid') + ' group by qualid').fetchall()
    waste_id = get_waste_id(resources)
    inven = isotope_calc(waste_id, snf_inventory, cur)
    return inven


def get_agent_ids(cursor, facility):
    """ Gets all agentIds from Agententry table for wanted facility

        agententry table has the following format:
            SimId / AgentId / Kind / Spec /
            Prototype / ParentID / Lifetime / EnterTime

    Parameters
    ---------
    cursor: cursor
        cursor for sqlite3

    Returns
    -------
    sink_id: array
        array of all the sink agentId values.
    """

    cur = cursor
    agent_id = []
    agent = cur.execute("select * from agententry where spec like '%" + facility + "%'").fetchall()

    for ag in agent:
        agent_id.append(ag[1])
    return agent_id


def get_waste_id(resource_array):
    """ Gets waste id from a resource array

    Parameters
    ---------
    resource_array: array
        array fetched from the resource table.

    Returns
    -------
    waste_id: array
        array of qualId for waste
    """

    wasteid = []

    # get all the wasteid
    for res in resource_array:
        wasteid.append(res[7])

    return set(wasteid)


def exec_string(array, search, whatwant):
    """ Generates sqlite query command to select things an
        inner join between resources and transactions.

    Parameters
    ---------
    array: array
        array of criteria that generates command
    search: str
        where [search]
        criteria for your search
    whatwant: str
        select [whatwant]
        column (set of values) you want out.

    Returns
    -------
    exec_str: str
        sqlite query command.
    """

    exec_str = ('select ' + whatwant + ' from resources inner join transactions\
                on transactions.resourceid = resources.resourceid where '
                + str(search) + ' = ' + str(array[0]))

    for ar in array[1:]:
        exec_str += ' and ' + str(ar)

    return exec_str


def get_sum(array, column_index):
    """ Returns sum of a column in an array

    Parameters:
    ---------
    array: array
        array that contains a column with numbers
    column_index: int
        index for the column to be summed
    """
    sum = 0
    for ar in array:
        sum += ar[column_index]

    return sum



def isotope_calc(wasteid_array, snf_inventory, cursor):
    """ Calculates isotope mass using mass fraction in compositions table.

        Fetches all from compositions table.
        Compositions table has the following format:
            SimId / QualId / NucId / MassFrac
        Then sees if the qualid matches, and if it multiplies
        the mass fraction by the snf_inventory.

    Prameters
    ---------
    wasteid_array: array
        array of qualid of wastes
    snf_inventory: float
        total mass of snf
    cursor: cursor
        cursor for sqlite3

    Returns
    -------
    nuclide_inven: array
        inventory of individual nuclides.
    """

    # Get compositions of different commodities
    # SimId / QualId / NucId / MassFrac
    cur = cursor
    comp = cur.execute('select * from compositions').fetchall()
    total_snf_mass = get_sum(snf_inventory, 0)

    nuclide_inven = 'total snf inventory = ' + str(total_snf_mass) + 'kg \n'
    nuclides = []
    mass_of_nuclides = []
    # if the 'qualid's match,
    # the nuclide quantity and calculated and displayed.
    for isotope in comp:
        for num in snf_inventory:
            # num[1] = snf inventory qualid 
            # isotope[1] = compositions qualid 
            if num[1] == isotope[1]:
                # num[0] = total mass of one composition
                # isotope[3] = mass fraction
                nuclide_quantity = num[0] * isotope[3]
                #isotope[2] = nucid
                nuclide_name = isotope[2]
                nuclides.append(nuclide_name)
                mass_of_nuclides.append(nuclide_quantity)

    nuclide_set = set(nuclides)
    mass_dict = collections.OrderedDict({})

    for nuclide in nuclide_set:
        temp_nuclide_sum = 0 
        for i in range(len(nuclides)):
            if nuclides[i] == nuclide:
                temp_nuclide_sum += mass_of_nuclides[i]
        mass_dict[nuclide] = temp_nuclide_sum


    for nuclide in mass_dict:
        nuclide_name = str(nucname.name(nuclide))
        nuclide_inven += nuclide_name + ' = ' + str(mass_dict[nuclide]) + 'kg \n'

    return nuclide_inven

def get_sim_time_duration(cursor):
    """ Returns simulation time and duration of the simulation

    Parameters
    ----------
    cursor: sqlite cursor

    Returns
    -------
    sim_time: int
        number of months in the simulation
    timestep: array
        linspace of timesteps in the simulation
    """
    cur = cursor
    sim_time = int(cur.execute('SELECT endtime FROM finish').fetchone()[0]) + 1
    timestep = np.linspace(0, sim_time, num=sim_time + 1)

    return sim_time, timestep


def isotope_mass_time_array(resources, compositions):
    """Creates an array with isotope name, mass, and time

    Parameters
    ----------
    resources: array
        resource data from the resources table
    compositions: array
        composition data from the compositions table

    Returns
    -------
    array
        isotope name array
    array
        isotope mass array
    array
        isotope transaction time array

    """

    temp_isotope = []
    temp_mass = []
    time_array = []

    for res in resources:
        for com in compositions:
            res_qualid = res[7]
            comp_qualid = com[1]
            if res_qualid == comp_qualid:
                nucid = com[2]
                mass_frac = com[3]
                mass_waste = res[5]
                res_time = res[16]
                temp_isotope.append(nucid)
                temp_mass.append(mass_frac*mass_waste) 
                time_array.append(res_time)

    return temp_isotope, temp_mass, time_array


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
    print(agent_ids)
    print(exec_string(agent_ids, 'transactions.senderid', '*'))
    if influx_bool is True:
        resources = cur.execute(exec_string(agent_ids,
                                            'transactions.receiverId',
                                            '*')).fetchall()
    else:
        resources = cur.execute(exec_string(agent_ids,
                                            'transactions.senderId',
                                            '*')).fetchall()
    compositions = cur.execute('SELECT * FROM compositions').fetchall()
    sim_time, timestep = get_sim_time_duration(cur)
    isotope, mass, time_array = isotope_mass_time_array(resources, compositions)

    waste_dict = get_waste_dict(isotope, mass, time_array, sim_time)

    multi_line_plot(waste_dict, timestep,
                    'Years', 'Mass [kg]',
                    title, outputname)


def get_waste_dict(isotope_array, mass_array, time_array, sim_time):
    """Given an isotope, mass and time array, creates a dictionary
       With key as isotope and time series of the isotope mass.

    Parameters
    ----------
    isotope_array: array
        array with all the isotopes from resources table
    mass_array: array
        array with all the mass values from resources table
    time_array: array
        array with all the time values from resources table
    sim_time: int
        simulation time

    Returns
    -------
    dict
        dictionary of mass time series of each unique isotope
    """

    waste_dict = collections.OrderedDict({})
    isotope_set = set(isotope_array)

    for iso in isotope_set:
        print(iso)
        mass = 0
        time_mass = []
        # at each timestep,
        for i in range(0, sim_time+1):
            # for each element in database,
            for x in range(0, len(isotope_array)):
                if i == time_array[x] and isotope_array[x] == iso:
                    mass += mass_array[x]
            time_mass.append(mass)
        waste_dict[iso] = time_mass

    return waste_dict



def capacity_calc(governments, timestep, entry, exit):
    """Adds and subtracts capacity over time for plotting

    Paramters
    ---------
    governments: array
        array of governments (countries)
    timestep: array
        array of timestep from 0 to simulation time
    entry: array
        power_cap, agentid, parentid, entertime
        of all entered reactors
    exit: array
        power_cap, agentid, parenitd, exittime
        of all decommissioned reactors

    Returns
    -------
    power_dict: dictionary
        dictionary of capacity progression with country_government as key
    num_dict: dictionary
        dictionary of number of reactors progression
        with country_government as key
    """

    power_dict = collections.OrderedDict({})
    num_dict = collections.OrderedDict({})

    for gov in governments:
        capacity = []
        num_reactors = []
        cap = 0
        count = 0
        for num in timestep:
            for enter in entry:
                if enter[3] == num and enter[2] == gov[1]:
                    cap += enter[0]
                    count += 1
            for dec in exit:
                if dec[3] == num and dec[2] == gov[1]:
                    cap -= dec[0]
                    count -= 1
            capacity.append(cap)
            num_reactors.append(count)

        power_dict[gov[0]] = np.asarray(capacity)
        num_dict[gov[0]] = np.asarray(num_reactors)

    return power_dict, num_dict

def multi_line_plot(dictionary, timestep, xlabel, ylabel, title, outputname):
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

    Returns
    -------
    stores a semilogy plot of dict data on path `outputname`
    """

    # set different colors for each bar
    color_index = 0
    prev = ''
    plot_array = []
    # for every country, create bar chart with different color
    for key in dictionary:
        # label is the name of the nuclide (converted from ZZAAA0000 format)
        label =  str(nucname.name(key))
        plt.semilogy(1950 + (timestep/12), dictionary[key],
                 color=cm.viridis(1.*color_index/len(dictionary)),
                 label=label)
        color_index += 1

    # plot
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.legend(loc=(1.0,0), prop={'size':10})
    plt.grid(True)
    plt.savefig(outputname, format='png', bbox_inches='tight')


def stacked_bar_chart(dictionary, timestep, xlabel, ylabel, title, outputname):
    """ Creates stacked bar chart of timstep vs dictionary

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
    Stacked bar chart
    """

    # set different colors for each bar
    color_index = 0
    top_index = True
    prev = ''
    plot_array = []
    # for every country, create bar chart with different color
    for key in dictionary:
        label = key.replace('_government', '')
        # very first country does not have a 'bottom' argument
        if top_index is True:
            plot = plt.bar(1950+(timestep/12), dictionary[key], .5,
                           color=cm.viridis(1.*color_index/len(dictionary)),
                           edgecolor='none', label=label)
            prev = dictionary[key]
            top_index = False
        # from the second country has 'bottom' argument
        else:
            plot = plt.bar(1950 + (timestep/12), dictionary[key], .5,
                           color=cm.viridis(1.*color_index/len(dictionary)),
                           edgecolor='none', bottom=prev, label=label)
            prev = np.add(prev, dictionary[key])
        plot_array.append(plot)
        color_index += 1

    # plot
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.legend(loc=(1.0,0))
    plt.grid(True)
    plt.savefig(outputname, format='png', bbox_inches='tight')


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
    sim_time, timestep = get_sim_time_duration(cur)
    powercap = []
    reactor_num = []
    countries = []
    cur = cursor
    # get power cap values
    governments = cur.execute('SELECT prototype, agentid FROM agententry\
                              WHERE spec = ":cycamore:DeployInst"').fetchall()

    entry = cur.execute('SELECT power_cap, agententry.agentid, parentid, entertime\
                        FROM agententry INNER JOIN\
                        agentstate_cycamore_reactorinfo\
                        ON agententry.agentid =\
                        agentstate_cycamore_reactorinfo.agentid').fetchall()

    exit = cur.execute('SELECT power_cap, agentexit.agentid, parentid, exittime\
                        FROM agentexit INNER JOIN\
                        agentstate_cycamore_reactorinfo\
                        ON agentexit.agentid =\
                        agentstate_cycamore_reactorinfo.agentid\
                        INNER JOIN agententry\
                        ON agentexit.agentid = agententry.agentid').fetchall()

    power_dict, num_dict = capacity_calc(governments, timestep, entry, exit)

    stacked_bar_chart(power_dict, timestep,
                      'Time', 'net_capacity',
                      'Net Capacity vs Time', 'power_plot.png')
    plt.figure()
    stacked_bar_chart(num_dict, timestep,
                      'Time', 'num_reactors',
                      'Number of Reactors vs Time', 'number_plot.png')



if __name__ == "__main__":
    file = sys.argv[1]
    con = lite.connect(file)
    with con:
        cur = con.cursor()
        # print(snf(cur))
        # plot_power(cur)
        plot_in_out_flux(cur, 'source', False, 'source vs time', 'source vs time')
        plt.figure()
        plot_in_out_flux(cur, 'sink', True, 'isotope vs time', 'isotope vs time')
  
