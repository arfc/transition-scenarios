import sqlite3 as lite
import sys
import matplotlib as plt

con = lite.connect('eu_crude.sqlite')

with con:

    cur = con.cursor()

    #initialized snf inventory
    snf_inventory=0
    
    # select all from transactions of commodity 'wasste'
    # SimId / TransactionId / SenderId / ReceiverId / ResourceId / Commodity / Time
    sink = cur.execute("select * from transactions where Commodity = 'waste' " ).fetchall()

    # create a list of all the resourceids that were sent to sink
    res_ids = []
    for tra in sink:
        res_ids.append(tra[4])

    #empty array for resources
    resources=[]

    # select resources that are in sink with res_id
    # append the resource data to array resources
    # SimId / ResourceId / ObjId / Type / TimeCreated / Quantity / Units / QualId / Parent1 / Parent2
    for res in res_ids:
        ik = cur.execute('select * from resources where ResourceId = ' + str(res)).fetchall()
        resources.append(ik[0])
        for row in ik:
            # adds quantity of snf to snf inventory
            snf_inventory += row[5]

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
                nuclide_name = str(isotope[2])
                print (nuclide_name + ' = ' + nuclide_quantity + ' kg')

    print(snf_inventory)
