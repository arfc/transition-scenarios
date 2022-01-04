import pandas as pd

import cymetric as cm
import transition_metrics as tm
reactors = ['xe100','mmr']
scenarios = ['nogrowth','1percent']

for reactor in reactors:
    for scenario in scenarios:
        outfile = f'../outputs/{reactor}_{scenario}.sqlite'

        transactions = tm.add_receiver_prototype(outfile)
        transactions.to_csv(f'{reactor}_{scenario}__transactions.csv')
