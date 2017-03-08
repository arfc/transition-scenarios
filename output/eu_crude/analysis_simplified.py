import sqlite3 as lite
import sys
import matplotlib as plt
from pyne import nucname

con = lite.connect('eu_crude.sqlite')

with con:

    cur = con.cursor()

    #initialized snf inventory
    snf_inventory=0
    
    # Get all sink agentIds 
    # SimId / AgentId / Kind / Spec / Prototype / ParentID / Lifetime / EnterTime
    sink_id = []
    agent = cur.execute("select * from agententry where spec like '%sink%'")

    for ag in agent:
        sink_id.append(ag[1])

    #empty array for resources
    resources=[]

    # fetch from resources table all the resources that are sent to sink. 
    get_waste_all_str = 'select * from resources inner join transactions on\
                         transactions.resourceid = resources.resourceid\
                         where transactions.receiverid = ' + str(sink_id[0])
    for sid in sink_id[1:]:
        get_waste_all_str += ' or ' + str(sid)

    get_waste_quantity_str = get_waste_all_str.replace('*', 'sum(quantity)')
    print(get_waste_quantity_str)

    resources = cur.execute(get_waste_all_str).fetchall()
    snf_inventory = cur.execute(get_waste_quantity_str).fetchall()[0][0]
    print(snf_inventory)
    # array of wasteid for later match
    wasteid = []

    # get all the wasteid 
    for res in resources:
        wasteid.append(res[7])

    # make it a set 
    wasteid = set(wasteid)

    # get compositions of different commodities
    # SimId / QualId / NucId / MassFrac
    comp = cur.execute('select * from compositions').fetchall()

    # if the 'qualid's match, the nuclide quantity and calculated and displayed.
    for isotope in comp:
        for num in wasteid:
            if num == isotope[1]:
                nuclide_quantity = str(snf_inventory*isotope[3])
                nuclide_name = str(nucname.name(isotope[2]))
                print (nuclide_name + ' = ' + nuclide_quantity + ' kg')

    print(snf_inventory)
