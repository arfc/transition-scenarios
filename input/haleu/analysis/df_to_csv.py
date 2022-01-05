import pandas as pd

import cymetric as cm
import transition_metrics as tm

def loop_over_scenarios():
    reactors = ['xe100','mmr']
    scenarios = ['nogrowth','1percent']

    for reactor in reactors:
        for scenario in scenarios:
            outfile = f'../outputs/{reactor}_{scenario}.sqlite'

            transactions = tm.add_receiver_prototype(outfile)
            transactions.to_csv(f'{reactor}_{scenario}_transactions.csv')

def single_scenario():
    scenario = 'current'
    outfile = f'../outputs/united_states_2020.sqlite'
    transactions = tm.add_receiver_prototype(outfile)
    transactions.to_csv(f'{scenario}_transactions.csv')


if __name__ == '__main__':
    single_scenario()
