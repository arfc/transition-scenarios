from functools import total_ordering
import numpy as np
import pandas as pd
import sqlite3

#import transition_metrics as tm

class Dakota_responses(object):
    '''
    Class of functions to get response functions for dakota 
    sensitiviy analysis.
    '''
    def __init__(self):
        self.adv_rxs = ['Xe-100','MMR','VOYGR']

def merge_and_fillna_col(left, right, lcol, rcol, how='inner', on=None):
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
    m = pd.merge(left, right, how=how, on=on)
    f = m[lcol].fillna(m[rcol])
    left[lcol] = f
    return left    

def get_table_from_output(db_file, table_name):
    '''
    Get a specified table from the SQlite database and return 
        it as a pandas dataframe
        
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
    agents = agent_entry[['SimId', 'AgentId', 'Kind', 'Spec', 'Prototype', 'ParentId',
                'Lifetime', 'EnterTime']]
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
            'SimId', 'Time', 'ResourceId'], how='inner')
    receiver_prototype = pd.merge(
        trans_resources, agents[['SimId', 'ReceiverId', 'Prototype']], on=[
            'SimId', 'ReceiverId']).sort_values(by=['Time', 'TransactionId']).reset_index(drop=True)
    return receiver_prototype  

def find_commodity_transactions(df, commodity):
    '''
    Finds all transactions involving a specified commodity

    Parameters:
    -----------
    df: dataframe
        dataframe of transactions
    commodity: str
        name of commodity to search for

    Returns:
    --------
    commodity_df: dataframe
        contains only transactions involving the specified commodity
    '''
    commodity_df = df.loc[df['Commodity'] == commodity]
    return commodity_df 

def find_prototype_transactions(df, prototype):
    '''
    Finds all transactions sent to a specified prototype

    Parameters:
    -----------
    df: dataframe
        dataframe of transactions
    prototype: str
        name of prototype to search for

    Returns:
    --------
    prototype_df: dataframe
        contains only transactions sent to the specified prototype
    '''
    prototype_df = df.loc[df['Prototype'] == prototype]
    return prototype_df

def commodity_to_prototype(transactions_df, commodity, prototype):
    '''
    Finds the transactions of a specific commodity sent to a single prototype in the simulation,
    modifies the time column, and adds in zeros for any time step without
    a transaction to the specified prototype, and sums all transactions for
    a single time step

    Parameters:
    -----------
    transactions_df: dataframe
        dataframe of transactions with the prototype name
        of the receiver agent added in. use add_receiver_prototype to get this
        dataframe
    commodity: str
        commodity of interest
    prototype: str
        name of prototype transactions are sent to

    Output:
    -------
    prototype_transactions: dataframe
        contains summed transactions at each time step that are sent to
        the specified prototype name.
    '''
    prototype_transactions = find_commodity_transactions(
        transactions_df, commodity)
    prototype_transactions = find_prototype_transactions(
        prototype_transactions, prototype)
    prototype_transactions = sum_and_add_missing_time(prototype_transactions)
    prototype_transactions = add_year(prototype_transactions)
    return prototype_transactions

def add_year(df):
    '''
    Adds column of Year, based on the Time colunm

    Parameters:
    -----------
    df: DataFrame
        DataFrame of data to add column to

    Returns:
    --------
    df: DataFrame
        DataFrame with the added column
    '''
    df['Year'] = np.round(df['Time'] / 12 + 1965, 2)
    df['Year'] = df['Year'].fillna(method='ffill')
    return df

def sum_and_add_missing_time(df):
    '''
    Sums the values of the same time step, and adds any missing time steps
    with 0 for the value

    Parameters:
    -----------
    df: dataframe
        dataframe

    Returns:
    --------
    summed_df: dataframe
        dataframe with the summed values for each time step and inserted
        missing time steps
    '''
    summed_df = df.groupby(['Time']).Quantity.sum().reset_index()
    summed_df = summed_df.set_index('Time').reindex(
        np.arange(0, 1500, 1)).fillna(0).reset_index()
    return summed_df

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
    '''
    transactions = add_receiver_prototype(db_file)
    adv_rxs = ['Xe-100','MMR','VOYGR']
    total_adv_rx_enriched_u = 0
    for reactor in adv_rxs:
        reactor_u = commodity_to_prototype(transactions, 
        'fresh_uox', reactor)
        total_adv_rx_enriched_u += reactor_u['Quantity']
    cumulative_u = total_adv_rx_enriched_u.cumsum()
    return cumulative_u.loc[cumulative_u.index[-1]]
