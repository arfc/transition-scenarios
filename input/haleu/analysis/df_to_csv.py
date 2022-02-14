import pandas as pd

import cymetric as cm
import transition_metrics as tm


def get_transactions_multiple_outputs():
    reactors = ['xe100', 'mmr']
    scenarios = ['nogrowth', '1percent']

    for reactor in reactors:
        for scenario in scenarios:
            outfile = f'../outputs/{reactor}_{scenario}.sqlite'

            transactions = tm.add_receiver_prototype(outfile)
            transactions.to_csv(f'{reactor}_{scenario}_transactions.csv')


def get_transactions_single_output():
    scenario = 'current'
    outfile = f'../outputs/united_states_2020.sqlite'
    transactions = tm.add_receiver_prototype(outfile)
    transactions.to_csv(f'{scenario}_transactions.csv')


if __name__ == '__main__':
    get_transactions_single_output()
