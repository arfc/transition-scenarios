# These functions outline different reactor deployment algorithms,
# and metrics for analyzing the final product.

import pandas as pd
import numpy as np
import math  # for rounding ceiling and floor
from datetime import datetime  # for random seed generation




# # # # # # # # # # # # Constituent Functions # # # # # # # # # # #

def direct_decom(df, ar_dict):
    """
    This function assumes that every time a reactor model is decommissioned it
    is replaced by a new version of itself.

    Parameters
    ----------
    df: pandas dataframe
        The dataframe of capacity information
    ar_dict: dictionary
        A dictionary of reactors with information of the form:
        {reactor: [Power (MWe), capacity_factor (%), lifetime (yr)]}
    """

    # now we are going to note when reactors are decommissioned
    for reactor in ar_dict.keys():
        # create a decommissioning column
        df[f'{reactor}Decom'] = 0
        for year in range(len(df['Year'])):
            decom_year = year + ar_dict[reactor][2]
            if decom_year >= len(df['Year']):
                pass
            else:
                # tracks the number of decommissioned reactors
                df.loc[decom_year, f'{reactor}Decom'] += df.loc[year, f'num_{reactor}']

                # construct new reactors to replace the decommissioned ones
                df.loc[decom_year, f'num_{reactor}'] += df.loc[year, f'num_{reactor}']

    return df

def num_react_to_cap(df, ar_dict):
    """
    This function takes in a dataframe and the dictionary of reactors,
    and converts the number of reactors columns to a capacity from each reactor
    and a total capacity column.

    Parameters
    ----------
    df: pandas dataframe
        The dataframe of capacity information
    ar_dict: dictionary
        A dictionary of reactors with information of the form:
        {reactor: [Power (MWe), capacity_factor (%), lifetime (yr)]}
    """

    if 'total_cap' not in df:
        df[f'total_cap'] = 0
        # Create a column for the new capacity each year.
        df['new_cap'] = 0
    else:
        pass

    for reactor in ar_dict.keys():
        # New capacity calculations.
        df[f'new_{reactor}_cap'] = (df[f'num_{reactor}'] - df[f'{reactor}Decom']) * ar_dict[f'{reactor}'][0]
        df['new_cap'] += df[f'new_{reactor}_cap']

        # Total capacity calculations.
        df[f'{reactor}_cap'] = df[f'num_{reactor}'] * ar_dict[f'{reactor}'][0]
        df['total_cap'] += df[f'{reactor}_cap']

    return df

