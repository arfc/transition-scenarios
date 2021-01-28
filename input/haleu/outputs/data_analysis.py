import cymetric as cym
import pandas as pd
#import dask.dataframe as dd


def materials(rsrcs, comps):
    """Materials metric returns the material mass (quantity of material in
    Resources times the massfrac in Compositions) indexed by the SimId, QualId,
    ResourceId, ObjId, TimeCreated, and NucId.
    """
    rsrcs = rsrcs[['SimId','ResourceId','ObjId','TimeCreated','Quantity','Units',\
        'QualId']]
    x = pd.merge(rsrcs, comps, on=['SimId', 'QualId'], how='inner')
    #x = x.set_index(['SimId', 'QualId', 'ResourceId', 'ObjId', 'TimeCreated',
    #                 'NucId', 'Units'])
    x['Mass'] = x['Quantity'] * x['MassFrac']
    #y.name = 'Mass'
    #z = y.reset_index()
    return x

db = cym.dbopen('united_states_2020.sqlite')
evaler = cym.Evaluator(db, write=False)
mat = materials(evaler.eval('Resources'),evaler.eval('Compositions'))
print(mat)