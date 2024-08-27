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


# # # # # # # # # # # # Deployment Functions # # # # # # # # # # #
# 1. Greedy Algorithm: deploy the largest reactor first at each time step, fill
#   in the remaining capacity with the next smallest, and so on.
# 2. Pre-determined distributions: one or more reactors have a preset
#   distribution, and a smaller capacity model fills in the gaps.
# 2.b Deployment Cap [extension of 2]: there is a single-number capacity for
#   one or more of the reactor models. * there is no function for this, just use
#   a constant distribution.
# 3. Random Deployment: uses a date and hour as seed to randomly sample the
#   reactors list.
# 4. Initially Random, Greedy: randomly deploys reactors until a reactor bigger
#   than the remaining capacity is proposed for each year, then fills remaining
#   capacity with a greedy algorithm.

def greedy_deployment(df, base_col, ar_dict):
    """
    In this greedy deployment, we will deploy the largest capacity reactor first until another deployment will exceed the desired capacity then the next largest capacity reactor is deployed and so on.

    Parameters
    ----------
    df: pandas dataframe
        The dataframe of capacity information
    base_col: str
        The string name corresponding to the column of capacity that the algorithm is deploying reactors to meet
    ar_dict: dictionary
        A dictionary of reactors with information of the form:
        {reactor: [Power (MWe), capacity_factor (%), lifetime (yr)]}
    """

    for reactor in ar_dict.keys():
        if f'num_{reactor}' not in df:
            df[f'num_{reactor}'] = 0
        else:
            pass

    for year in range(len(df[base_col])):
        remaining_cap = df[base_col][year].copy()
        for reactor in ar_dict.keys():
            if ar_dict[reactor][0] > remaining_cap:
                reactor_div = 0
            else:
                # find out how many of this reactor to deploy
                reactor_div = math.floor(remaining_cap / ar_dict[reactor][0])
            # remaining capacity to meet
            remaining_cap -= reactor_div * ar_dict[reactor][0]
            df.loc[year, f'num_{reactor}'] += reactor_div

    # account for decommissioning with a direct replacement
    df = direct_decom(df, ar_dict)

    # Now calculate the total capacity each year (includes capacity from a
    # replacement reactor that is new that year, but not new overall because it
    # is replacing itself).
    df  = num_react_to_cap(df, ar_dict)

    return df


def pre_det_deployment(df, base_col, ar_dict, greedy=True):
    """
    This function allows the user to specify a distribution for reactor
    deployment for specific models.

    There are two implementations:
    1) greedy (greedy=True): wherein the largest reactor is deployed up till
    its cap, then the next largest and so on.
    2) linear (greedy=False): wherein the capped reactors are cyclically
    deployed until they hit their individual cap.

    df: pandas dataframe
        The dataframe of capacity information.
    base_col: str
        The string name corresponding to the column of capacity that the
        algorithm is deploying reactors to meet.
    ar_dict: dictionary
        A dictionary of reactors with information of the form:
        {reactor: [Power (MWe), capacity_factor (%), lifetime (yr),
        [distribution]]}.
        * The distribution must be the same length as the capacity you are
        matching.
        * The function assumes that the distribution is at the third index
        (i.e., fourth spot).
    greedy: bool
        A True/False value that determines whether the initial deployment is
        greedy or linear.
    """
    # initialize the number of reactor columns
    for reactor in ar_dict.keys():
        if f'num_{reactor}' not in df:
            df[f'num_{reactor}'] = 0
        else:
            pass

    if greedy == True:
        for year in range(len(df[base_col])):
            cap_difference = df[base_col][year].copy()
            for reactor in ar_dict.keys():
                # The number of reactors you'd need to meet the remaining
                # capacity.
                most_reactors = math.floor(cap_difference/ar_dict[reactor][0])
                # If there is a distribution we'll use it. Otherwise, we
                # will use a greedy deployment.
                if type(ar_dict[reactor][3]) == list:
                    # Check if the desired amount is greater than the cap.
                    if most_reactors >= ar_dict[reactor][3][year]:
                        # If so, we will only deploy up to the cap.
                        cap_difference -= ar_dict[reactor][3][year] * ar_dict[reactor][0]
                        df.loc[year, f'num_{reactor}'] += ar_dict[reactor][3][year]
                    # If the desired is less than the cap, then we'll deploy a
                    # greedy amount of reactors.
                    else:
                        cap_difference -= most_reactors * ar_dict[reactor][0]
                        df.loc[year, f'num_{reactor}'] += most_reactors
                # If there's no cap then we'll deploy a greedy amount of
                # reactors.
                else:
                    cap_difference -= most_reactors * ar_dict[reactor][0]
                    df.loc[year, f'num_{reactor}'] += most_reactors
    # Not greedy.
    else:
        for year in range(len(df[base_col])):
            cap_difference = df[base_col][year].copy()
            while cap_difference > 0:
                for reactor in ar_dict.keys():
                    # Check if the next reactor will exceed or equal the
                    # desired capacity.
                    next_difference = cap_difference - ar_dict[reactor][0]
                    # Set the limit one of the smallest reactors below zero
                    # so the while loop can end.
                    if next_difference <= -(ar_dict[reactor][0] + 1):
                        continue
                    else:
                        # Check if a cap exists.
                        if type(ar_dict[reactor][3]) == list:
                            # Check if the cap will be exceeded by adding
                            # another reactor.
                            if ar_dict[reactor][3][year] >= (df.loc[year,f'num_{reactor}'] + 1):
                                df.loc[year, f'num_{reactor}'] += 1
                                # Update remaining capacity to be met.
                                cap_difference -= ar_dict[reactor][0]
                        # If there isn't a cap add another reactor.
                        else:
                            df.loc[year, f'num_{reactor}'] += 1
                            # Update remaining capacity to be met.
                            cap_difference -= ar_dict[reactor][0]

    # account for decommissioning with a direct replacement
    df = direct_decom(df, ar_dict)

    # Now calculate the total capacity each year (includes capacity from a
    # replacement reactor that is new that year, but not new overall because it
    # is replacing itself).
    df  = num_react_to_cap(df, ar_dict)

    return df


