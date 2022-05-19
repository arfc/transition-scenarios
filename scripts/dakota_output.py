from functools import total_ordering
import pandas as pd

import cymetric as cym
import transition_metrics as tm

class Dakota_responses(object):
    '''
    Class of functions to get response functions for dakota 
    sensitiviy analysis.
    '''
    def __init__(self):
        self.adv_rxs = ['Xe-100','MMR','VOYGR']

def get_enriched_u_mass(db_file, transition_start):
    '''
    Calculates the cumulative and average monthly mass of enriched 
    uranium sent to advanced reactors in a simulation. The average 
    is calculated from the start of the transition to the end of the 
    simulation (time step 1500).

    Parameters:
    -----------
    db_file: str
        name of database file
    transition_start: int
        time step the modeled transition begins at
    Returns:
    --------
    cumulative_u: float
        cumulative mass of enriched uranium sent to advanced reactors
    average_u: float
        average monthly mass of enriched uranium sent to advanced reactors
    '''
    transactions = tm.add_receiver_prototype(db_file)
    total_adv_rx_enriched_u = 0
    for reactor in self.adv_rxs:
        reactor_u = tm. commodity_to_prototype(transactions, 
        'fresh_uox', reactor)
        total_adv_rx_enriched_u += reactor_u['Quantity']
    cumulative_u = total_adv_rx_enriched_u.cum()
    average_u = total_adv_rx_enriched_u[transition_start:].mean()
    return (cumulative_u, average_u)
