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


def rx_commission_decommission(filename, non_lwr):
    '''
    Creates DataFrame with time dependent totals of each
    prototype in the simulation. Adds column for the total
    number of LWR duirng the simulation

    Parameters:
    -----------
    filename: str
        string of file name, relative path to this notebook
    non_lwr: list of str
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
    comm = comm.rename(index=str, columns={'EnterTime': 'Time'})
    comm = tools.add_missing_time_step(comm, time)
    c = comm.pivot('Time', 'Prototype')['Count'].reset_index()

    if decomm is not None:
        # make exit counts negative for plotting purposes
        neg = -decomm['Count']
        decomm = decomm.drop('Count', axis=1)
        decomm = pd.concat([decomm, neg], axis=1)
        decomm.rename(columns={'ExitTime': 'Time'}, inplace=True)
        d = decomm.pivot('Time', 'Prototype')['Count'].reset_index()
        simulation_data = pd.merge(
            c,
            d,
            left_on='Time',
            right_on='Time',
            how='outer',
            sort=True,
            suffixes=(
                '_enter',
                '_exit')).fillna(0)
    else:
        simulation_data = c.fillna(0)

    simulation_data = simulation_data.set_index('Time')
    simulation_data['lwr_total'] = simulation_data.drop(
        non_lwr, axis=1).sum(
        axis=1)
    simulation_data['lwr_total'] = simulation_data['lwr_total'].cumsum()

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
    df['Year'] = pd.Series(
        [np.nan for x in range(len(df.index))], index=df.index)
    for index, row in df.iterrows():
        # if df['Time'][index] % 12 == 1:
        df['Year'][index] = np.round(df['Time'][index] / 12 + 1965, 2)
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
    dataframe[columns].plot(x=columns[0], legend=False)

    l = plt.legend(fontsize=12)
    for ii in range(3, len(labels)):
        l.get_texts()[ii - 3].set_text(labels[ii])
    l.set_title(labels[2])
    plt.setp(l.get_title(), fontsize=12)

    plt.xlabel(labels[0], fontsize=18)
    plt.ylabel(labels[1], fontsize=18)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)

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
    transactions = evaler.eval(
        'TransactionQuantity').sort_values(by='TimeCreated')
    transactions = transactions.rename(columns={'TimeCreated': 'Time'})
    transactions = tools.add_missing_time_step(
        transactions, evaler.eval('TimeList'))
    return transactions


def commodity_mass_traded(transactions, commodity):
    '''
    Calculates the total amount of a commodity traded
    at each time step

    Parameters:
    -----------
    transactions: dataframe
        dataframe of transactions of the simulation
    commodity: str
        commodity name

    Outputs:
    --------
    total_commodity: DataFrame
        DataFrame of total amount of each
        commodity traded as a function of time
    '''
    transactions[commodity] = transactions.loc[transactions['Commodity']
                                               == commodity]['Quantity']
    transactions[commodity].fillna(value=0, inplace=True)
    total_commodity = transactions[['Time', commodity, 'Units']]
    total_commodity = total_commodity.groupby(total_commodity['Time']).aggregate(
        {commodity: 'sum', 'Units': 'first'}).reset_index()
    total_commodity = add_year(total_commodity)
    return total_commodity


def add_receiver_prototype(filename):
    '''
    Creates dataframe of transactions information, and adds in
    the prototype name corresponding to the ReceiverId of the
    transaction. This dataframe is merged with the Agents dataframe, with the
    AgentId column renamed to ReceivedId to assist the merge process.

    Parameters:
    -----------
    filename: str
        database filename

    Outputs:
    --------
    receiver_prototype: dataframe
        contains all of the transactions with the prototype name of the
        receiver included
    '''
    transactions = get_transactions(filename)
    evaler = get_metrics(filename)
    agents = evaler.eval('Agents')
    agents = agents.rename(columns={'AgentId': 'ReceiverId'})
    receiver_prototype = pd.merge(
        transactions, agents, on=[
            'SimId', 'ReceiverId'])
    return receiver_prototype


def transactions_to_prototype(transactions_df, prototype):
    '''
    Extracts the transactions sent to a single prototype in the simulation,
    modifies the time column, and adds in zeros for any time step without
    a transaction to the specified prototype, and sums all transactions for
    a single time step

    Parameters:
    -----------
    transactions_df: dataframe
        dataframe of transactions with the prototype name
        of the receiver agent added in.
    prototype: str
        name of prototype transactions are sent to

    Output:
    -------
    prototype_transactions: dataframe
        contains summed transactions at each time step that are sent to
        the specified prototype name.
    '''
    prototype_transactions = add_year(transactions_df)
    prototype_transactions = prototype_transactions.loc[
        prototype_transactions['Prototype'] == prototype]
    prototype_transactions = prototype_transactions.groupby(
        ['Year']).Quantity.sum().reset_index()
    prototype_transactions = prototype_transactions.set_index('Year').reindex(
        np.round(np.arange(1965, 2090, 0.08333), 2)).fillna(0).reset_index()
    return prototype_transactions


def commodity_to_LWR(transactions_df, commodity, prototype):
    '''
    Finds all of the transactions of a commodity name to
    the LWRs in the simulation, adds in zeros for any time step without
    a transaction to the LWRs, and sums all transactions for
    a single time step

    Parameters:
    -----------
    transactions_df: dataframe
        transactions data
    commodity: str
        commodity of interest
    prototype: str
        name of other reactor prototypes in the simulation

    Outputs:
    --------
    lwr_transactions: dataframe
        contains the transactions to the LWRs of the specified
        commodity, year information is included
    '''
    lwr_transactions = add_year(transactions_df)
    lwr_transactions = lwr_transactions.loc[lwr_transactions['Commodity'] == 
            commodity]
    lwr_transactions = lwr_transactions.loc[
        lwr_transactions['Prototype'] != prototype]
    lwr_transactions = lwr_transactions.groupby(
        ['Year']).Quantity.sum().reset_index()
    lwr_transactions = lwr_transactions.set_index('Year').reindex(
        np.round(np.arange(1965, 2090, 0.08333), 2)).fillna(0).reset_index()
    return lwr_transactions


def commodity_to_prototype(transactions_df, commodity, prototype):
    '''
    Finds the transactions of a specific commodity sent to a single prototype 
    in the simulation, modifies the time column, and adds in zeros for any 
    time step without a transaction to the specified prototype, and sums all 
    transactions for a single time step

    Parameters:
    -----------
    transactions_df: dataframe
        dataframe of transactions with the prototype name
        of the receiver agent added in.
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
    prototype_transactions = add_year(transactions_df)
    prototype_transactions = prototype_transactions.loc[
        prototype_transactions['Commodity'] == commodity]
    prototype_transactions = prototype_transactions.loc[
        prototype_transactions['Prototype'] == prototype]
    prototype_transactions = prototype_transactions.groupby(
        ['Year']).Quantity.sum().reset_index()
    prototype_transactions = prototype_transactions.set_index('Year').reindex(
        np.round(np.arange(1965, 2090, 0.08333), 2)).fillna(0).reset_index()
    return prototype_transactions


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
        merged_df = pd.merge(merged_df, ii, on=['Time', 'Year'])

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
    v = (2 * x_i - 1) * np.log(x_i / (1 - x_i))
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
    SWU = P * separation_potential(x_p) + T * separation_potential(x_t) - \
        F * separation_potential(x_f)
    return SWU


def calculate_tails(product, x_p, x_t, x_f):
    '''
    Calculates the mass of tails based on
    a mass of product and the mass fraction
    of the roduct, tails, and feed

    Parameters:
    ----------
    product: int, Series
        mass of product
    x_p: float
        mass fraction of product
    x_t: float
        mass fraction of tails
    x_f: float
        mass fraction of feed

    Outputs:
    -------
    tails: int, Series
    '''
    tails = (x_f - x_p) * product / (x_t - x_f)
    return tails


def calculate_feed(product, tails):
    '''
    Calculates the mass of feed material required
    to produce a given amount of product and
    tails

    Parameters:
    ----------
    product: int, Series
        mass of product
    tails: int, Series
        mass of tails

    Outputs:
    --------
    feed: int, Series
        mass of feed material
    '''
    feed = product + tails
    return feed


def get_electricity(filename):
    '''
    Gets the time dependent electricity output of reactors
    in the silumation

    Parameters:
    -----------
    filename: str
        name of database to be parsed

    Outputs:
    --------
    electricity_output: DataFrame
        time dependent electricity output, includes
        column for year of time step. The energy column
        is in units of GWe-yr, causing the divide by 1000
        operation.
    '''
    evaler = get_metrics(filename)
    electricity = evaler.eval('AnnualElectricityGeneratedByAgent')
    electricity['Year'] = electricity['Year'] + 1965
    electricity_output = electricity.groupby(
        ['Year']).Energy.sum().reset_index()
    electricity_output['Energy'] = electricity_output['Energy'] / 1000

    return electricity_output


def get_prototype_energy(filename, advanced_rx):
    '''
    Calculates the annual electricity produced by a given
    prototype name by merging the Agents and AnnualElectricityGeneratedByAgent
    dataframes so that agents can be grouped by prototype name

    Parameters:
    -----------
    filename: str
        name of database file
    advanced_rx: str
        name of advanced reactor prototype

    Outputs:
    --------
    prototype_energy: dataframe
        dataframe of the year and the total amount of electricity
        generated by all agents of the given prototype name. Values
        are in units of GWe-y, causing the divide by 1000 operation
    '''
    evaler = get_metrics(filename)
    agents = evaler.eval('Agents')
    energy = evaler.eval('AnnualElectricityGeneratedByAgent')
    merged_df = pd.merge(energy, agents, on=['SimId', 'AgentId'])
    merged_df['Year'] = merged_df['Year'] + 1965
    prototype_energy = merged_df.loc[merged_df['Prototype'] == advanced_rx]
    prototype_energy = prototype_energy.groupby(
        ['Year']).Energy.sum().reset_index()
    prototype_energy = prototype_energy.set_index(
        'Year').reindex(range(1965, 2091)).fillna(0).reset_index()
    prototype_energy['Energy'] = prototype_energy['Energy'] / 1000
    return prototype_energy


def get_lwr_energy(filename, advanced_rx):
    '''
    Calculates the annual electricity produced by a given
    prototype name by merging the Agents and AnnualElectricityGeneratedByAgent
    dataframes so that agents can be grouped by prototype name

    Parameters:
    -----------
    filename: str
        name of database file
    advanced_rx: str
        name of advanced reactor prototype also present in the simulation

    Outputs:
    --------
    lwr_energy: dataframe
        dataframe of the year and the total amount of electricity
        generated by all of the LWRs in the simulation. The energy
        column is in units of GWe-y, causing the divide by 1000
        operation.
    '''
    evaler = get_metrics(filename)
    agents = evaler.eval('Agents')
    energy = evaler.eval('AnnualElectricityGeneratedByAgent')
    merged_df = pd.merge(energy, agents, on=['SimId', 'AgentId'])
    merged_df['Year'] = merged_df['Year'] + 1965
    lwr_energy = merged_df.loc[merged_df['Prototype'] != advanced_rx]
    lwr_energy = lwr_energy.groupby(['Year']).Energy.sum().reset_index()
    lwr_energy = lwr_energy.set_index('Year').reindex(
        range(1965, 2091)).fillna(0).reset_index()
    lwr_energy['Energy'] = lwr_energy['Energy'] / 1000
    return lwr_energy
