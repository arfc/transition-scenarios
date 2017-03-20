import sqlite3 as lite
import sys
from pyne import nucname
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

if len(sys.argv) < 2:
    print('Usage: python analysis.py [cylus_output_file]')


def snf(filename):
    """ prints total snf and isotope mass

    Parameters
    ----------
    filename: int
        cyclus output file to be analyzed.

    Returns
    -------
    Returns total snf and isotope mass.
    """

    sink_id = get_sink_agent_ids()
    resources = cur.execute(exec_string(sink_id, 'transactions.receiverId', '*')).fetchall()
    snf_inventory = cur.execute(exec_string(sink_id, 'transactions.receiverId', 'sum(quantity)')).fetchall()[0][0]
    waste_id = get_waste_id(resources)
    inven = isotope_calc(waste_id, snf_inventory)
    return inven


def get_sink_agent_ids():
    """ Gets all sink agentIds from Agententry table.

        agententry table has the following format:
            SimId / AgentId / Kind / Spec /
            Prototype / ParentID / Lifetime / EnterTime

    Parameters
    ---------
    none

    Returns
    -------
    sink_id: array
        array of all the sink agentId values.
    """

    sink_id = []
    agent = cur.execute("select * from agententry where spec like '%sink%'")

    for ag in agent:
        sink_id.append(ag[1])
    return sink_id


def get_waste_id(resource_array):
    """ Gets waste id from a resource array

    Paramters
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


def get_colors():
    """ Gets colors from a matplotlib dictionary

    Parameters
    ----------
    None

    Returns
    -------
    Colors: array
        array of color hex codes
    """

    colors = []
    for hex in matplotlib.colors.cnames.items():
        colors.append(hex[1])
    return colors


def get_power(filename):
    """ Gets capacity vs time for every country
        in stacked bar chart.

    Parameters
    ----------
    filename: file
        cyclus output file used

    Returns
    -------
    plot of net capapcity vs time

    """

    sim_time = int(cur.execute('select endtime from finish').fetchone()[0]) + 1
    timestep = np.linspace(0, sim_time, num=sim_time + 1)
    powercap = []
    reactor_num = []
    countries = []
    # get power cap values

    governments = cur.execute('sELECT prototype, agentid FROM agententry\
                              WHERE spec = ":cycamore:DeployInst"').fetchall()

    entry = cur.execute('sELECT power_cap, agententry.agentid, parentid, entertime\
                        FROM agententry INNER JOIN\
                        agentstate_cycamore_reactorinfo\
                        ON agententry.agentid =\
                        agentstate_cycamore_reactorinfo.agentid').fetchall()

    exit = cur.execute('sELECT power_cap, agentexit.agentid, parentid, exittime\
                        FROM agentexit INNER JOIN\
                        agentstate_cycamore_reactorinfo\
                        ON agentexit.agentid =\
                        agentstate_cycamore_reactorinfo.agentid\
                        INNER JOIN agententry\
                        ON agentexit.agentid = agententry.agentid').fetchall()

    # create empty array for each country_government
    for gov in governments:
        exec(gov[0] + '_power = []', globals())
        exec(gov[0] + '_num = []', globals())
        countries.append(gov[0])

    # add and subtract capacity and num for every government
    # for every timestep for every entry and exit
    for gov in governments:
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
            exec(gov[0] + '_power.append(cap)')
            exec(gov[0] + '_num.append(count)')

    colors = get_colors()

    # set different colors for each bar
    index = 0
    top_index = 0
    prev_govs = ''

    # plot string for the legend
    plot_string = 'plt.legend(('

    # convert power arrays to numpy arrays for stacking
    for gov in governments:
        exec(gov[0] + '_power = np.asarray(' + gov[0] + '_power)')

    # for every country, create bar chart with different color
    for gov in governments:
        color = colors[index]
        # very first country does not have a 'bottom' argument
        if top_index == 0:
            exec(
                gov[0] + '_plot = plt.bar( 1950+(timestep/12), '
                + gov[0] + '_power, .5, color = color,\
                edgecolor = "none")'
                )
            prev_govs = gov[0] + '_power'
        # from the second country has 'bottom' argument
        else:
            exec(
                gov[0] + '_plot = plt.bar( 1950+(timestep/12), '
                + gov[0] + '_power, .5, color = color,\
                edgecolor = "none", bottom =' + prev_govs + ')'
                )
            prev_govs += '+ ' + gov[0] + '_power'

        plot_string += gov[0] + '_plot,'
        index += 1
        top_index += 1

    # generate string for exec of plt.lengend
    plot_string = plot_string[:-1]
    plot_string += '), ('
    for gov in governments:
        plot_string += "'" + gov[0] + "', "
    plot_string = plot_string[:-2]
    plot_string += '))'

    # plot
    plt.ylabel('Net Installed Capacity')
    plt.title('Capacity of EU Reactors vs Time')
    exec(plot_string)
    plt.grid(True)
    plt.show()


def time_vs_waste(filename):
    """ Generates time vs waste
    """


def exec_string(array, search, whatwant):
    """ Generates sqlite query command to select things an
        inner join between resources and transactions.

    Parmaters
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
        exec_str += ' or ' + str(ar)

    return exec_str


def isotope_calc(wasteid_array, snf_inventory):
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
        total mass of snf_inventory

    Returns
    -------
    nuclide_inven: array
        inventory of individual nuclides.
    """

    # Get compositions of different commodities
    # SimId / QualId / NucId / MassFrac
    comp = cur.execute('select * from compositions').fetchall()

    nuclide_inven = ['total snf inventory = ' + str(snf_inventory) + 'kg']
    # if the 'qualid's match,
    # the nuclide quantity and calculated and displayed.
    for isotope in comp:
        for num in wasteid_array:
            if num == isotope[1]:
                nuclide_quantity = str(snf_inventory*isotope[3])
                nuclide_name = str(nucname.name(isotope[2]))
                nuclide_inven.append(nuclide_name + ' = ' + nuclide_quantity)

    return nuclide_inven


if __name__ == "__main__":
    file = sys.argv[1]
    con = lite.connect(file)

    with con:
        cur = con.cursor()
        print(snf(file))
        get_power(file)
