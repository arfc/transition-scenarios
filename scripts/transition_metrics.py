import numpy as np
import pandas as pd
import math

import dataframe_analysis as dfa
import cymetric as cym
from cymetric import tools
from cymetric import timeseries
from cymetric import filters


def get_metrics(db_file):
    '''
    Opens database using cymetric and evaluates metrics

    Parameters:
    -----------
    db_file: str
        SQLite database from Cyclus

    Returns:
    --------
    metrics_evaler: Evaluator object
        contains all of the metrics of the database
    '''

    db = cym.dbopen(db_file)
    metrics_evaler = cym.Evaluator(db, write=False)
    return metrics_evaler


def get_lwr_totals(db_file, non_lwr_prototypes):
    '''
    Creates DataFrame with the number of each prototype
    commissioned or decommissioned at each time step,
    then a column to report the total number of LWR
    prototypes deployed at each time step. The LWR
    prototypes are all of different names, based on
    the unit name, so the aren't easy to total, and
    there are far more LWR prototype names than non-LWR
    prototype names.

    Parameters:
    -----------
    db_file: str
        SQLite database from Cyclus
    non_lwr_prototypes: list of str
        names of non LWR prototypes in the simulation

    Returns:
    --------
    simulation_data: DataFrame
        Contains the number of each prototype commissioned
        and decommissioned at each time step and a column
        for the total number of LWR prototypes at each
        time step.
    '''
    evaler = get_metrics(db_file)
    time = evaler.eval('TimeList')

    commission_df = evaler.eval('BuildSeries')
    decommission_df = evaler.eval('DecommissionSeries')
    commission_df = commission_df.rename(
        index=str, columns={'EnterTime': 'Time'})
    commission_df = tools.add_missing_time_step(commission_df, time)
    commission_by_prototype = pd.pivot_table(
        commission_df,
        values='Count',
        index='Time',
        columns='Prototype',
        fill_value=0)
    commission_by_prototype = dfa.add_zeros_columns(
        commission_by_prototype, non_lwr_prototypes)
    commission_by_prototype['lwr'] = commission_by_prototype.drop(
        non_lwr_prototypes, axis=1).sum(axis=1)
    commission_by_prototype = commission_by_prototype.astype('float64')

    if decommission_df is not None:
        negative_count = -decommission_df['Count']
        decommission_df = decommission_df.drop('Count', axis=1)
        decommission_df = pd.concat([decommission_df, negative_count], axis=1)
        decommission_df.rename(columns={'ExitTime': 'Time'}, inplace=True)
        decommission_by_prototype = decommission_df.pivot(index='Time', columns='Prototype')[
            'Count'].reset_index()
        decommission_by_prototype = dfa.add_zeros_columns(
            decommission_by_prototype, non_lwr_prototypes)
        decommission_by_prototype = decommission_by_prototype.set_index('Time')
        decommission_by_prototype['lwr'] = decommission_by_prototype.drop(
            non_lwr_prototypes, axis=1).sum(axis=1)
        decommission_by_prototype = decommission_by_prototype.reset_index()
        simulation_data = pd.merge(
            commission_by_prototype,
            decommission_by_prototype,
            left_on='Time',
            right_on='Time',
            how='outer',
            sort=True,
            suffixes=(
                '_enter',
                '_exit')).fillna(0)
    else:
        simulation_data = commission_by_prototype.fillna(0)
        simulation_data = simulation_data.add_suffix('_enter')
        for column in simulation_data.columns:
            simulation_data[(column[:-5] + 'exit')] = 0.0
    simulation_data['lwr_total'] = (
        simulation_data['lwr_enter'] +
        simulation_data['lwr_exit']).cumsum()
    return simulation_data.reset_index()


def get_prototype_totals(db_file, non_lwr_prototypes, prototypes):
    '''
    This function performs the get_lwr_totals
    function on a provided database. Then the total number of
    each prototype deployed at a given time is calculated and
    added to the dataframe. If a prototype
    name is specified but not in the dataframe, then a column
    of zeros is added with the column name reflecting the
    prototype name.

    Parameters:
    -----------
    db_file: str
        name of SQLite database from Cyclus
    non_lwr_prototypes: list of str
        names of non LWR prototypes in the simulation
    prototypes: list of str
        list of names of prototypes to be summed together

    Returns:
    --------
    prototypes_df : DataFrame
        enter, exit, and totals for each type of prototype
        specified. Includes a column totaling all of the
        spcified prototypes, labeled as `advrx_enter`,
        `advrx_exit`, and `advrx_total`, because it is assumed
        that prototypes specified will be the advanced reactors
        of interest for the transition modeled.
    '''
    prototypes_df = get_lwr_totals(db_file, non_lwr_prototypes)
    prototypes_df = dfa.add_year(prototypes_df)
    prototypes_df['advrx_enter'] = 0.0
    prototypes_df['advrx_total'] = 0.0
    for prototype in prototypes:
        if prototype in prototypes_df.columns:
            prototypes_df = prototypes_df.rename(
                columns={prototype: prototype + '_enter'})
            prototypes_df[prototype +
                          '_exit'] = np.zeros(
                                              len(prototypes_df[prototype +
                                                                '_enter']))
        prototypes_df[prototype +
                      '_total'] = (prototypes_df[prototype +
                                                 '_enter'] +
                                   prototypes_df[prototype +
                                                 '_exit']).cumsum()
        prototypes_df['advrx_enter'] += prototypes_df[prototype + '_enter']
        prototypes_df['advrx_total'] += prototypes_df[prototype + '_total']

    return prototypes_df

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
    evaler = get_metrics(db_file)
    agents = evaler.eval('Agents')
    agents = agents.rename(columns={'AgentId': 'ReceiverId'})
    resources = evaler.eval('Resources')
    resources = resources[['SimId', 'ResourceId', 'ObjId', 'TimeCreated',
                           'Quantity', 'Units']]
    resources = resources.rename(columns={'TimeCreated': 'Time'})
    transactions = evaler.eval('Transactions')
    trans_resources = pd.merge(
        transactions, resources, on=[
            'SimId', 'Time', 'ResourceId'], how='inner')
    receiver_prototype = pd.merge(
        trans_resources, agents[['SimId', 'ReceiverId', 'Prototype']], on=[
            'SimId', 'ReceiverId']).sort_values(by=['Time', 'TransactionId']).reset_index(drop=True)
    receiver_prototype = receiver_prototype.rename(
        columns={'Prototype': 'ReceiverPrototype'})
    return receiver_prototype


def get_annual_electricity(db_file):
    '''
    Gets the time dependent annual electricity output of reactors
    in the silumation

    Parameters:
    -----------
    db_file: str
        SQLite database from Cyclus

    Returns:
    --------
    electricity_output: DataFrame
        time dependent electricity output, includes
        column for year of time step. The energy column
        is in units of GWe-yr, causing the divide by 1000
        operation.
    '''
    evaler = get_metrics(db_file)
    electricity = evaler.eval('AnnualElectricityGeneratedByAgent')
    electricity['Year'] = electricity['Year'] + 1965
    electricity_output = electricity.groupby(
        ['Year']).Energy.sum().reset_index()
    electricity_output['Energy'] = electricity_output['Energy'] / 1000

    return electricity_output


def get_monthly_electricity(db_file):
    '''
    Gets the time dependent monthy electricity output of reactors
    in the silumation

    Parameters:
    -----------
    db_file: str
        SQLite database from Cyclus

    Returns:
    --------
    electricity_output: DataFrame
        time dependent electricity output, includes
        column for year of time step. The energy column
        is in units of GWe-yr, causing the divide by 1000
        operation.
    '''
    evaler = get_metrics(db_file)
    electricity = evaler.eval('MonthlyElectricityGeneratedByAgent')
    electricity['Year'] = electricity['Month'] / 12 + 1965
    electricity_output = electricity.groupby(
        ['Year']).Energy.sum().reset_index()
    electricity_output['Energy'] = electricity_output['Energy'] / 1000

    return electricity_output


def get_prototype_energy(db_file, advanced_rx):
    '''
    Calculates the annual electricity produced by a given
    prototype name by merging the Agents and AnnualElectricityGeneratedByAgent
    dataframes so that agents can be grouped by prototype name

    Parameters:
    -----------
    db_file: str
        SQLite database from Cyclus
    advanced_rx: str
        name of advanced reactor prototype

    Returns:
    --------
    prototype_energy: dataframe
        dataframe of the year and the total amount of electricity
        generated by all agents of the given prototype name. Values
        are in units of GWe-y, causing the divide by 1000 operation
    '''
    evaler = get_metrics(db_file)
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


def get_lwr_energy(db_file, advanced_rx):
    '''
    Calculates the annual electricity produced by a given
    prototype name by merging the Agents and AnnualElectricityGeneratedByAgent
    dataframes so that agents can be grouped by prototype name

    Parameters:
    -----------
    db_file: str
        SQLite database from Cyclus
    advanced_rx: list of str
        name(s) of advanced reactor prototype also present in the simulation

    Returns:
    --------
    lwr_energy: dataframe
        dataframe of the year and the total amount of electricity
        generated by all of the LWRs in the simulation. The energy
        column is in units of GWe-y, causing the divide by 1000
        operation.
    '''
    evaler = get_metrics(db_file)
    agents = evaler.eval('Agents')
    energy = evaler.eval('AnnualElectricityGeneratedByAgent')
    merged_df = pd.merge(energy, agents, on=['SimId', 'AgentId'])
    merged_df['Year'] = merged_df['Year'] + 1965
    lwr_energy = merged_df.loc[~merged_df['Prototype'].isin(advanced_rx)]
    lwr_energy = lwr_energy.groupby(['Year']).Energy.sum().reset_index()
    lwr_energy = lwr_energy.set_index('Year').reindex(
        range(1965, 2091)).fillna(0).reset_index()
    lwr_energy['Energy'] = lwr_energy['Energy'] / 1000
    return lwr_energy
