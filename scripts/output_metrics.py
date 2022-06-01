from functools import total_ordering
import numpy as np
import pandas as pd
import sqlite3

import dataframe_analysis as dfa

class Dakota_responses(object):
    '''
    Class of functions to get response functions for dakota 
    sensitiviy analysis.
    '''
    def __init__(self):
        self.adv_rxs = ['Xe-100','MMR','VOYGR']

def merge_and_fillna_col(left, right, lcol, rcol, how='left', on=None):
    """Merges two dataframes and fills the values of the left column
    with the values from the right column. A copy of left is returned.

    Parameters
    ----------
    left : pd.DataFrame
        The left data frame
    right : pd.DataFrame
        The right data frame
    lcol : str
        The left column name
    rcol : str
        The right column name
    how : str, optional
        How to perform merge, same as in pd.merge()
    on : list of str, optional
        Which columns to merge on, same as in pd.merge()
    """
    merged_df = left.reset_index().merge(right, how=how).set_index('index')
    fill_column = merged_df[lcol].fillna(merged_df[rcol])
    left[lcol] = fill_column
    return left    

def get_table_from_output(db_file, table_name):
    '''
    Get a specified table from the SQlite database and return 
    it as a pandas dataframe. The dataframe for the 'Resources' 
    uses only select columns from that table because of memory 
    issues expereinced, and only the columns called here were 
    used for later functions.
        
        Parameters:
        -----------
        db_file: str
            filename of database
        table_name: str
            name of table in dataframe
        
        Returns:
        --------
        table_df: DataFrame
            requested table from database
        '''
    connect = sqlite3.connect(db_file)
    if table_name == 'Resources':
        table_df = pd.read_sql_query('SELECT SimId, ResourceId, ObjId, TimeCreated, Quantity, Units FROM Resources', connect)
    else:
        table_df = pd.read_sql_query('SELECT * FROM ' + table_name, connect)
    return table_df

def create_agents_table(db_file):
    '''
        Recreates the Agents metric in cymetric
        
        Parameters:
        -----------
        db_file: str
            filename of database
        
        Returns:
        --------
        agents: DataFrame
            recreated Agents metric
    '''
    agent_entry = get_table_from_output(db_file, 'AgentEntry')
    agent_exit = get_table_from_output(db_file, 'AgentExit')
    info = get_table_from_output(db_file, 'Info')
    decom_schedule = get_table_from_output(db_file, 'DecomSchedule')
    mergeon = ['SimId', 'AgentId']
    agents = agent_entry.copy()
    agents['ExitTime'] = [np.nan]*len(agent_entry)
    if agent_exit is not None:
        agent_exit.columns = ['SimId', 'AgentId', 'Exits']
        agents = merge_and_fillna_col(agents, agent_exit[['SimId', 'AgentId', 'Exits']],
                                        'ExitTime', 'Exits', on=mergeon)
    if decom_schedule is not None:
        agents = merge_and_fillna_col(agents, decom_schedule[['SimId', 'AgentId',
                                               'DecomTime']],
                                       'ExitTime', 'DecomTime', on=mergeon)
    agents = merge_and_fillna_col(agents, info[['SimId', 'Duration']],
                                    'ExitTime', 'Duration', on=['SimId'])  
    return agents  

def add_receiver_prototype(db_file):
    '''
    Creates dataframe of transactions information, and adds in
    the prototype name corresponding to the ReceiverId of the
    transaction. This dataframe is merged with the Agents dataframe, with the
    AgentId column renamed to ReceivedId to assist the merge process. The
    final dataframe is organized by ascending order of Time then TransactionId

    Parameters:
    -----------
    db_file: str
        SQLite database from Cyclus

    Returns:
    --------
    receiver_prototype: dataframe
        contains all of the transactions with the prototype name of the
        receiver included
    '''
    agents = create_agents_table(db_file)
    agents = agents.rename(columns={'AgentId': 'ReceiverId'})
    resources = get_table_from_output(db_file, 'Resources')
    resources = resources.rename(columns={'TimeCreated': 'Time'})
    transactions = get_table_from_output(db_file, 'Transactions')
    trans_resources = pd.merge(
        transactions, resources, on=[
            'ResourceId'])
    #trans_resources = trans_resources.drop_duplicates(subset='TransactionId').reset_index(drop=True)
    trans_resources = trans_resources.drop(columns=['SimId_y', 'Time_y'])
    trans_resources = trans_resources.rename(columns={'Time_x':'Time',
                                                    'SimId_x':'SimId'})
    receiver_prototype = pd.merge(
        trans_resources, agents[['SimId', 'ReceiverId', 'Prototype']], on=[
            'SimId', 'ReceiverId']).sort_values(by=['Time', 'TransactionId']).reset_index(drop=True)
    return receiver_prototype  

def get_multiple_prototype_transactions(db_file, prototypes, commodity):
    '''
    Gets the transactions of the given commodity sent to the
    specified prototypes in each time step

    Parameters:
    -----------
    db_file: str
        name of database file
    prototypes: list of strs
        names of prototypes to get transactions to
    commodity: str
        name of commodity
    
    Returns:
    --------
    commodity_transactions: DataFrame
        DataFrame of transactions for commodity to specific prototypes.
        The mass sent to each prototype is in a separate column, with
        the name of the column matching the prototype name.
    '''
    transactions = add_receiver_prototype(db_file)
    commodity_transactions = pd.DataFrame(columns=prototypes)
    for prototype in prototypes:
        commodity_transactions[prototype] = dfa.commodity_to_prototype(transactions, 
        commodity, prototype)['Quantity']
    return commodity_transactions

def get_enriched_u_mass(db_file, prototypes, transition_start):
    '''
        Calculates the cumulative mass of enriched 
        uranium sent to given prototypes in a simulation. The average 
        is calculated from the start of the transition to the end of the 
        simulation.

        Parameters:
        -----------
        db_file: str
            name of database file
        prototypes: list of str
            names of prototypes to find transactions to
        transition_start: int
            time step the modeled transition begins at
        
        Returns:
        --------
        cumulative_u: float
            cumulative mass of enriched uranium sent to specified protopyes
            starting at the transition start time. 
    '''
    enriched_u_df = get_multiple_prototype_transactions(db_file, prototypes, 'fresh_uox')
    total_adv_rx_enriched_u = 0
    for prototype in prototypes:
        total_adv_rx_enriched_u += enriched_u_df[prototype]
    cumulative_u = total_adv_rx_enriched_u[int(transition_start):].cumsum()
    return cumulative_u.loc[cumulative_u.index[-1]]

def calculate_swu(db_file, prototypes, transition_start, assays):
    '''
    Calculates the cumulative amount of SWU capacity required to 
    create the enriched uranium in the simulation

    Parameters:
    -----------
    db_file: str
        name of database file
    prototypes: list of strs
        names of prototypes to consider in calculation
    transition_start: int
        time step the modeled transition begins at
    assays: dict
        dictionary of the prototype names and the uranium assay for 
        the fuel for the prototype, form of the dictionary is
        {prototype name(str):assay(float)}. This dictionary MUST 
        contain the assays for the tails and feed streams, and be labeled 
        as 'tails' and 'feed'. 
    
    Returns:
    --------
    cumulative_swu: float
        The total cumulative swu capacity required for the simulation, 
        starting at the transition start time. 
    '''
    enriched_u_mass = get_multiple_prototype_transactions(db_file, prototypes, 'fresh_uox')
    swu = 0
    for prototype in prototypes:
        tails = dfa.calculate_tails(enriched_u_mass[prototype], assays[prototype],
        assays['tails'], assays['feed'])
        feed = dfa.calculate_feed(enriched_u_mass[prototype], tails)
        prototype_swu = dfa.calculate_SWU(enriched_u_mass[prototype], assays[prototype],
        tails, assays['tails'], feed, assays['feed'])
        swu += prototype_swu
    cumulative_swu = swu[int(transition_start):].cumsum()
    return np.round(cumulative_swu.loc[cumulative_swu.index[-1]],2)

def get_waste_discharged(db_file, prototypes, transition_start, commodities):
    '''
    Gets the mass of fuel discharged from specified prototypes, 
    sums them together and provides a sumulative total from the start 
    of the transition. 

    Parameters:
    -----------
    db_file: str
        name of database file
    prototypes: list of strs
        names of prototypes
    transition_start: int or float
        time step the transition starts at
    commodities: dict of strs
        name of waste commodity for each prototype, in the form
        {prototype name (str): commodity name(str)}
    
    Returns: 
    --------
    waste_discharged: float
        cumulative waste discharged from all specified prototypes
    '''
    transactions = add_receiver_prototype(db_file)
    waste = 0
    for prototype in prototypes:
        waste += dfa.commodity_mass_traded(transactions,
                                           commodities[prototype])['Quantity']
    waste_discharged = waste[int(transition_start):].cumsum()
    return waste_discharged.loc[waste_discharged.index[-1]]

