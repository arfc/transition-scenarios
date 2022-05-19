from functools import total_ordering
import numpy as np
import pandas as pd
import sqlite3

import transition_metrics as tm

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

    def get_table_from_output(self, db_file, table_name):
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
        table_df = pd.read_sql_query('SELECT * FROM ' + table_name, connect)
        return table_df

    def create_agents_table(self, db_file):
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
        agent_entry = self.get_table_from_output(self, db_file, 'AgentEntry')
        agent_exit = self.get_table_from_output(self, db_file, 'AgentExit')
        info = self.get_table_from_output(self, db_file, 'Info')
        decom_schedule = self.get_table_from_output(self, db_file, 'DecomSchedule')
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

    def get_enriched_u_mass(self, db_file, transition_start):
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
        transactions = self.create_agents_table(self, db_file)
        total_adv_rx_enriched_u = 0
        for reactor in self.adv_rxs:
            reactor_u = tm. commodity_to_prototype(transactions, 
            'fresh_uox', reactor)
            total_adv_rx_enriched_u += reactor_u['Quantity']
        cumulative_u = total_adv_rx_enriched_u.cum()
        average_u = total_adv_rx_enriched_u[transition_start:].mean()
        return (cumulative_u, average_u)
