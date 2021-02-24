import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math 

import cymetric as cym
from cymetric import tools
from cymetric import timeseries
from cymetric import filters

def get_metrics(filename):
    '''
    Opens database using cymetric and evaluates metrics
    
    Parameters:
    -----------
    filename: str
        relative path of database
        
    Outputs:
    --------
    evaler: Evaluator object
        contains all of the metrics of the database
    '''
    
    db = cym.dbopen(filename)
    evaler = cym.Evaluator(db, write=False)
    return evaler


def rx_commission_decommission(filename, nonreactors):
    '''
    Creates new column for the total number of 
    each reactor type duirng a specified simulation
    
    Parameters:
    -----------
    filename: str
        string of file name, relative path to this notebook
    nonreactors: list of str
        names of nonreactor facilities in the simulation
        
    Returns:
    simulation_data: DataFrame
        Reactor data of the simulation with the additional 
        columns of reactor totals
    '''
    evaler = get_metrics(filename)
    time = evaler.eval('TimeList')
    
    comm = evaler.eval('BuildSeries')
    decomm = evaler.eval('DecommissionSeries')

    # make exit counts negative for plotting purposes
    neg = -decomm['Count']
    decomm = decomm.drop('Count', axis=1)
    decomm = pd.concat([decomm, neg], axis=1)

    # for later merge, rename time columns
    comm = comm.rename(index=str, columns={'EnterTime':'Time'})
    decomm.rename(columns={'ExitTime' : 'Time'}, inplace =True)
    comm = tools.add_missing_time_step(comm, time)

    # pivot tables for plotting purposes, and merge tables
    c = comm.pivot('Time', 'Prototype')['Count'].reset_index()
    d = decomm.pivot('Time', 'Prototype')['Count'].reset_index()
    simulation_data = pd.merge(c, d, left_on='Time', right_on='Time', how='outer', sort=True,
        suffixes=('_enter', '_exit')).fillna(0)
    
    
    simulation_data = simulation_data.set_index('Time')
    simulation_data['reactor_total'] = simulation_data.drop(nonreactors, axis=1).sum(axis=1)
    simulation_data['reactor_total'] = simulation_data['reactor_total'].cumsum()
     
    return simulation_data.reset_index()


def add_year(df):
    '''
    Adds column of Year, based on the Time colunm
    
    Parameters:
    -----------
    df: DataFrame
        DataFrame of data to add column to
        
    Outputs:
    --------
    df: DataFrame 
        DataFrame with the added column
    '''
    df['Year'] = pd.Series([np.nan for x in range(len(df.index))], index=df.index)
    for index, row in df.iterrows():
        if df['Time'][index] % 12 == 1:
            df['Year'][index] = df['Time'][index-1]/12 + 1965
    df['Year'] = df['Year'].fillna(method='ffill')
    return df


def plot_metric(dataframe, columns, labels=['Time', 'Count', 'metric']):
    '''
    Plots line graph of the specified column from the given 
    DataFrame as a function of time.
    
    Parameters:
    -----------
    dataframe: DataFrame
        data from simulation
    columns: list of str
        names of columns to be plotted, first element
        is the x-axis
    labels: list of str
        label names in the order: 
            1. x-axis label
            2. y-axis label
            3. Legend title
            4-end. legend labels
    
    Outputs:
    --------
    Figure of desired metric as a function of time
    '''
    dataframe[columns].plot(x = columns[0], figsize=(20, 10), legend=False)
    
    l = plt.legend()
    for ii in range(3,len(labels)):
        l.get_texts()[ii-3].set_text(labels[ii])
    l.set_title(labels[2])
    
    plt.xlabel(labels[0], fontsize=18)
    plt.ylabel(labels[1], fontsize=18)
    
    return 

def get_transactions(filename):
    '''
    Gets the TransactionQuantity metric from cymetric, 
    sorts by TimeCreated, and renames the TimeCreated 
    column
    
    Parametrs:
    ----------
    filename: str
        relative path to database
        
    Outputs:
    --------
    transactions: DataFrame
        transaction data with specified modifications    
    '''
    evaler = get_metrics(filename)
    transactions = evaler.eval('TransactionQuantity').sort_values(by='TimeCreated')
    transactions = transactions.rename(columns={'TimeCreated':'Time'})
    transactions = tools.add_missing_time_step(transactions, evaler.eval('TimeList'))
    return transactions


def calculate_throughput(filename, commodity):
    '''
    Calculates the total amount of a commodity traded 
    at each time step
    
    Parameters:
    -----------
    filename: str
        database file name
    commodity: str
        commodity name
    
    Outputs:
    --------
    total_commodity: DataFrame
        DataFrame of total amount of each 
        commodity traded as a function of time
    '''
    transactions = get_transactions(filename)
    transactions[commodity] = transactions.loc[transactions['Commodity']==commodity]['Quantity']
    transactions[commodity].fillna(value=0, inplace=True)
    total_commodity = transactions[['Time',commodity,'Units']]
    total_commodity = total_commodity.groupby(total_commodity['Time']
                                             ).aggregate({commodity:'sum', 'Units':'first'}).reset_index()
    total_commodity = add_year(total_commodity)
    return total_commodity

def merge_databases(dfs):
    '''
    merges multiple dataframes based on Time and Year columns
    
    Parameters:
    -----------
    dfs: list of DataFrames
        names of DataFrames to be merged
    
    Outputs:
    --------
    merged_df: DataFrame
        final DataFrame comprosed of all merged 
        DataFrames
    '''
    merged_df = pd.DataFrame({'Time': np.linspace(0, 1499, 1500)})
    merged_df = add_year(merged_df)
    for ii in dfs:
        merged_df = pd.merge(merged_df, ii, on=['Time','Year'])
    
    return merged_df

def separation_potential(x_i):
    '''
    Calculates Separation Potentail, for use in calculating 
    Separative Work Units (SWU) required for enrichment level
    
    Inputs:
    -------
    x_i: int
        mass fraction of a generic mass stream
    
    Returns:
    --------
    v: int
        Separation potential
    '''
    v = (2*x_i - 1) * np.log(x_i/(1-x_i))
    return v
    
def calculate_SWU(P, x_p, T, x_t, F, x_f):
    '''
    Calculates Separative Work Units required to produce
    throughput of product given mass of feed and tails and
    assay of each mass stream
    
    Parameters:
    -----------
    P: int, Series
        mass of product
    x_p: int
        weight percent of U-235 in product
    T: int, Series
        mass of tails
    x_t: int
        weight percent of U-235 in tails
    F: int, Series
        mass of feed
    x_f: int
        weight percent of U-235 in feed
    
    Outputs:
    --------
    SWU: int
        Separative Work units per unit time 
    '''
    SWU = P*separation_potential(x_p) + T*separation_potential(x_t) - \
          F*separation_potential(x_f)
    return SWU