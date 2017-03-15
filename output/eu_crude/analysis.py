import sqlite3 as lite
import sys
from pyne import nucname

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
            SimId / AgentId / Kind / Spec / Prototype / ParentID / Lifetime / EnterTime

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

    exec_str = 'select ' + whatwant + ' from resources inner join transactions\
                on transactions.resourceid = resources.resourceid where ' + str(search) + ' = ' + str(array[0])

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
    # if the 'qualid's match, the nuclide quantity and calculated and displayed.
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
