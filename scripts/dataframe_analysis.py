import numpy as np
import pandas as pd


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

def add_zeros_columns(df, column_names):
    '''
    Adds a column of a specified name to a given dataframe
    if a column of that name does not exist already. The
    added column is of the length of the entire dataframe
    but consists of only zeros. This function allows for
    greater flexibility in defining prototypes of
    interest across multiple tranistion scenarios

    Parameters:
    -----------
    df: DataFrame
        dataframe to add column to, if the column doesn't exist
        already
    column_names: list of strs
        names to be checked for existence and added if missing

    Returns:
    --------
    df: DataFrame
        dataframe with added column, if column doesn't
        exist anymore
    '''
    for item in column_names:
        if item not in df.columns:
            df[item] = 0.0
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

def find_prototype_receiver(df, prototype):
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
    prototype_df = df.loc[df['ReceiverPrototype'] == prototype]
    return prototype_df

def find_prototype_sender(df, prototype):
    '''
    Finds all transactions sent from a specified prototype

    Parameters:
    -----------
    df: dataframe
        dataframe of transactions
    prototype: str
        name of prototype to search for

    Returns:
    --------
    prototype_df: dataframe
        contains only transactions sent from the specified prototype
    '''
    prototype_df = df.loc[df['SenderPrototype'] == prototype]
    return prototype_df

def commodity_mass_traded(transactions_df, commodity):
    '''
    Calculates the total amount of a commodity traded
    at each time step

    Parameters:
    -----------
    transactions: dataframe
        dataframe of transactions of the simulation
    commodity: str
        commodity name

    Returns:
    --------
    total_commodity: DataFrame
        DataFrame of total amount of each
        commodity traded as a function of time
    '''
    transactions = find_commodity_transactions(transactions_df, commodity)
    transactions = sum_and_add_missing_time(transactions)
    total_commodity = add_year(transactions)
    return total_commodity

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
    prototype_transactions = find_prototype_receiver(
        prototype_transactions, prototype)
    prototype_transactions = sum_and_add_missing_time(prototype_transactions)
    prototype_transactions = add_year(prototype_transactions)
    return prototype_transactions

def commodity_from_prototype(transactions_df, commodity, prototype):
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
    prototype_transactions = find_prototype_sender(
        prototype_transactions, prototype)
    prototype_transactions = sum_and_add_missing_time(prototype_transactions)
    prototype_transactions = add_year(prototype_transactions)
    return prototype_transactions

def commodity_to_LWR(transactions_df, commodity, prototype):
    '''
    Finds the transactions of a specific commodity sent to the LWRs in the
    simulation, modifies the time column, and adds in zeros for any time step
    without a transaction to the LWRs, and sums all transactions for
    a single time step

    Parameters:
    -----------
    transactions_df: dataframe
        dataframe of transactions with the prototype name
        of the receiver agent added in. use add_receiver_prototype to get this
        dataframe
    commodity: str
        commodity of interest
    prototype: list of str
        name(s) of non-LWR reactor prototype(s) in the simulation

    Output:
    -------
    prototype_transactions: dataframe
        contains summed transactions at each time step that are sent to
        the specified prototype name.
    '''
    prototype_transactions = find_commodity_transactions(
        transactions_df, commodity)
    prototype_transactions = prototype_transactions[
        ~prototype_transactions['ReceiverPrototype'].isin(prototype)]
    prototype_transactions = sum_and_add_missing_time(prototype_transactions)
    prototype_transactions = add_year(prototype_transactions)
    return prototype_transactions

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

    Returns:
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

    Returns:
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

    Returns:
    --------
    feed: int, Series
        mass of feed material
    '''
    feed = product + tails
    return feed