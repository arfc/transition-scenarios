import pandas as pd
import sys
import cymetric as cm
import cProfile

sys.path.insert(0,'../../../scripts')
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
    profile = cProfile.Profile()
    profile.enable()
    scenario = 'current'
    outfile = f'../../../../toy_problems/cyclus_inputs/noDI_arma.sqlite'
    transactions = tm.add_receiver_prototype(outfile)
    transactions.to_csv(f'{scenario}_transactions.csv')
    profile.disable()
    profile.print_stats()


if __name__ == '__main__':
    get_transactions_single_output()
