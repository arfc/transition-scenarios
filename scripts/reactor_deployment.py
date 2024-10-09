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
    df: :class:`pandas.DataFrame`
        The dataframe of capacity information
    ar_dict: dictionary
        A dictionary of reactors with information of the form:
        {reactor: [Power (MWe), capacity_factor (%), lifetime (yr)]}

    Returns
    -------
    df: :class:`pandas.DataFrame`
        The dataframe of capacity information with the decommissioned reactors.
    """

    # define number of years
    num_years = len(df['Year'])

    # now we are going to note when reactors are decommissioned
    for reactor in ar_dict.keys():
        # create a decommissioning column
        df[f'{reactor}Decom'] = 0
        for year in range(num_years):
            decom_year = year + ar_dict[reactor][2]
            if decom_year >= num_years:
                pass
            else:
                # tracks the number of decommissioned reactors
                df.loc[decom_year, f'{reactor}Decom'] += \
                    df.loc[year, f'num_{reactor}']

                # construct new reactors to replace the decommissioned ones
                df.loc[decom_year, f'num_{reactor}'] += \
                    df.loc[year, f'num_{reactor}']

    return df


def num_react_to_cap(df, ar_dict):
    """
    This function takes in a dataframe and the dictionary of reactors,
    and converts the number of reactors columns to a capacity from each reactor
    and a total capacity column.

    Parameters
    ----------
    df: :class:`pandas.DataFrame`
        The dataframe of capacity information
    ar_dict: dictionary
        A dictionary of reactors with information of the form:
        {reactor: [Power (MWe), capacity_factor (%), lifetime (yr)]}

    Returns
    -------
    df: :class:`pandas.DataFrame`
        The dataframe of capacity information with the new columns.
    """

    if 'total_cap' not in df:
        df[f'total_cap'] = 0
        # Create a column for the new capacity each year.
        df['new_cap'] = 0
    else:
        pass

    for reactor in ar_dict.keys():
        # New capacity calculations.
        df[f'new_{reactor}_cap'] = (df[f'num_{reactor}'] -
                                    df[f'{reactor}Decom']) * \
                                    ar_dict[f'{reactor}'][0]
        df['new_cap'] += df[f'new_{reactor}_cap']

        # Total capacity calculations.
        df[f'{reactor}_cap'] = df[f'num_{reactor}'] * ar_dict[f'{reactor}'][0]
        df['total_cap'] += df[f'{reactor}_cap']

    return df


def reactor_columns(df, ar_dict):
    """
    This function takes in a dataframe and the dictionary of reactors,
    and creates columns for each reactor.

    Parameters
    ----------
    df: :class:`pandas.DataFrame`
        The dataframe of capacity information.
    ar_dict: dictionary
        A dictionary of reactors with information of the form:
        {reactor: [Power (MWe), capacity_factor (%), lifetime (yr)]}

    Returns
    -------
    df: :class:`pandas.DataFrame`
        The dataframe of capacity information with columns for each reactor.
    """

    # Initialize the number of reactor columns.
    for reactor in ar_dict.keys():
        if f'num_{reactor}' not in df:
            df[f'num_{reactor}'] = 0
        else:
            pass

    return df


# # # # # # # # # # # # Deployment Functions # # # # # # # # # # #
# 1. Greedy Algorithm: deploy the largest reactor first at each time step, fill
#   in the remaining capacity with the next smallest, and so on.
# 2. Pre-determined distributions: one or more reactors have a preset
#   distribution, and a smaller capacity model fills in the gaps.
# 2.b Deployment Cap [extension of 2]: there is a single-number capacity for
#   one or more of the reactor models. * there is no function for this, just
#   use a constant distribution.
# 3. Random Deployment: uses a date and hour as seed to randomly sample the
#   reactors list.
# 4. Initially Random, Greedy: randomly deploys reactors until a reactor bigger
#   than the remaining capacity is proposed for each year, then fills remaining
#   capacity with a greedy algorithm.

def greedy_deployment(df, base_col, ar_dict, dep_start_year):
    """
    In this greedy deployment, we will deploy the largest capacity reactor
    first until another deployment will exceed the desired capacity then the
    next largest capacity reactor is deployed and so on.

    Parameters
    ----------
    df: :class:`pandas.DataFrame`
        The dataframe of capacity information
    base_col: str
        The string name corresponding to the column of capacity that the
        algorithm is deploying reactors to meet
    ar_dict: dictionary
        A dictionary of reactors with information of the form:
        {reactor: [Power (MWe), capacity_factor (%), lifetime (yr)]}
    dep_start_year: int
        The year to start the deployment of advanced reactors.

    Returns
    -------
    df: :class:`pandas.DataFrame`
        The dataframe of capacity information with the deployed reactors.

    Notes
    -----
    * This function assumes that there is a column called 'Year' that is not
    the column of indices.
    """

    # Initialize the number of reactor columns.
    df = reactor_columns(df, ar_dict)

    start_index = df[df['Year'] == dep_start_year].index[0]

    for year in range(start_index, len(df[base_col])):
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
    df = num_react_to_cap(df, ar_dict)

    return df


def pre_det_deployment(df, base_col, ar_dict, dep_start_year, greedy=True):
    """
    This function allows the user to specify a distribution for reactor
    deployment for specific models.

    There are two implementations:
    1) greedy (greedy=True): wherein the largest reactor is deployed up till
    its cap, then the next largest and so on.
    2) linear (greedy=False): wherein the capped reactors are cyclically
    deployed until they hit their individual cap.


    Parameters
    ----------
    df: :class:`pandas.DataFrame`
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
    dep_start_year: int
        The year to start the deployment of advanced reactors.
    greedy: bool
        A True/False value that determines whether the initial deployment is
        greedy or linear.

    Returns
    -------
    df: :class:`pandas.DataFrame`
        The dataframe of capacity information with the deployed reactors.

    Notes
    -----
    * This function assumes that there is a column called 'Year' that is not
    the column of indices.
    """
    # initialize the number of reactor columns
    df = reactor_columns(df, ar_dict)

    start_index = df[df['Year'] == dep_start_year].index[0]

    if greedy is True:
        for year in range(start_index, len(df[base_col])):
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
                        cap_difference -= ar_dict[reactor][3][year] \
                                          * ar_dict[reactor][0]
                        df.loc[year, f'num_{reactor}'] += \
                            ar_dict[reactor][3][year]
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
        for year in range(start_index, len(df[base_col])):
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
                            if ar_dict[reactor][3][year] >= \
                              (df.loc[year, f'num_{reactor}'] + 1):
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
    df = num_react_to_cap(df, ar_dict)

    return df


def rand_deployment(df, base_col, ar_dict, dep_start_year,
                    set_seed=False, rough=True, tolerance=5):
    """
    This function randomly deploys reactors from the dictionary of
    reactors to meet a capacity need.

    There are two implementations:
    1) rough (rough=True): if a reactor greater than the remaining
    capacity is proposed, the deployment ends.
    2) [IN-PROGRESS] complete (rough=False): the algorithm keeps
    trying to deploy randomly selected reactors until the capacity demand
    has been met.

    Parameters
    ----------
    df: :class:`pandas.DataFrame`
        The dataframe of capacity information.
    base_col: str
        The string name corresponding to the column of capacity that the
        algorithm is deploying reactors to meet.
    ar_dict: dictionary
        A dictionary of reactors with information of the form:
        {reactor: [Power (MWe), capacity_factor (%), lifetime (yr)]}.
    dep_start_year: int
        The year to start the deployment of advanced reactors.
    set_seed: bool
        A True/False value that determines whether the seed used for the random
        number is set or varies based on time.
    rough: bool
        A True/False value that determines whether the initial deployment is
        rough or complete.
    tolerance: float/int
        The capacity tolerance to which reactors are deployed in the complete
        deployment case (i.e., when rough=False). Without this, convergence
        is tricky to achieve.

    Returns
    -------
    df: :class:`pandas.DataFrame`
        The dataframe of capacity information with the deployed reactors.

    Notes
    -----
    * This function assumes that there is a column called 'Year' that is not
    the column of indices.
    """

    # initialize the number of reactor columns
    df = reactor_columns(df, ar_dict)

    start_index = df[df['Year'] == dep_start_year].index[0]

    for year in range(start_index, len(df[base_col])):
        years_capacity = df[base_col][year]
        # I set the limit this way so that something close to 0 could still
        # deploy the smallest reactor.

        if set_seed is False:
            # sample random number based on time
            c = datetime.now()
            real_seed = int(c.strftime('%y%m%d%H%M%S'))
        else:
            real_seed = 20240527121205

        rng = np.random.default_rng(seed=real_seed)

        while years_capacity > -(ar_dict[list(ar_dict.keys())[-1]][0] + 1):
            rand_reactor = rng.integers(0, len(ar_dict.keys()))

            # identify random reactor
            deployed = list(ar_dict.keys())[rand_reactor]

            if ar_dict[deployed][0] > years_capacity:
                if rough is True:
                    # for a much rougher check, use break
                    break
                elif rough is False:
                    # for a more accurate, but much much longer run
                    # todo, finish this ensuring it can converge
                    raise NotImplementedError('This feature is unstable.')
                    continue
            else:
                df.loc[year, f'num_{deployed}'] += 1
                years_capacity -= ar_dict[deployed][0]

    # account for decommissioning with a direct replacement
    df = direct_decom(df, ar_dict)

    # Now calculate the total capacity each year (includes capacity from a
    # replacement reactor that is new that year, but not new overall because it
    # is replacing itself).
    df = num_react_to_cap(df, ar_dict)

    return df


def rand_greedy_deployment(df, base_col, ar_dict,
                           dep_start_year, set_seed=False):
    """
    This function combines the rough random and greedy deployments
    to fill in any gaps caused by the roughness.

    Parameters
    ----------
    df: :class:`pandas.DataFrame`
        The dataframe of capacity information.
    base_col: str
        The string name corresponding to the column of capacity that the
        algorithm is deploying reactors to meet.
    ar_dict: dictionary
        A dictionary of reactors with information of the form:
        {reactor: [Power (MWe), capacity_factor (%), lifetime (yr)]}.
    dep_start_year: int
        The year to start the deployment of advanced reactors.
    set_seed: bool
        A True/False value that determines whether the seed used for the random
        number is set or varies based on time.

    Returns
    -------
    df: :class:`pandas.DataFrame`
        The dataframe of capacity information with the deployed reactors.

    Notes
    -----
    * This function assumes that there is a column called 'Year' that is not
    the column of indices.
    """
    # Initialize the number of reactor columns.
    df = reactor_columns(df, ar_dict)

    # First we will apply the rough random.
    df = rand_deployment(df, base_col, ar_dict,
                         dep_start_year, set_seed, rough=True)

    # Now we will make a remaining cap column.
    df['remaining_cap'] = df[base_col] - df['new_cap']

    # make columns for the randomly deployed reactors and the greedy reactors
    for reactor in ar_dict.keys():
        df[f'greedy_num_{reactor}'] = 0
        df[f'rand_num_{reactor}'] = df[f'num_{reactor}']

    # Now we will use the remaining cap column with a greedy deployment.
    df = greedy_deployment(df, 'remaining_cap', ar_dict, dep_start_year)

    # reset the total capacity column
    df['new_cap'] = 0

    # populate the greedy reactor column
    for year in range(len(df[base_col])):
        for reactor in ar_dict.keys():
            df.loc[year, f'greedy_num_{reactor}'] = \
                   df.loc[year, f'num_{reactor}'] \
                   - df.loc[year, f'rand_num_{reactor}']
            df.loc[year, f'new_cap'] += df.loc[year, f'{reactor}_cap']

    return df


# # # # # # # # # # # # Analysis Functions # # # # # # # # # # # #
# analyze how well each method did with the amount and percent of over/
# under-prediction.

def simple_diff(df, base, proj):
    """
    Calculate the difference between the projected and base capacities.

    Parameters
    ----------
    df: :class:`pandas.DataFrame`
        The output pandas DataFrame from the deployment functions.
    base: str
        The name of the base capacity column in the DataFrame.
    proj: str
        The name of the projected capacity column in the DataFrame.
    """
    return df[proj] - df[base]


def calc_percentage(df, base):
    """
    Calculate the percentage difference between proj and base.

    Parameters
    ----------
    df: :class:`pandas.DataFrame`
        The output pandas DataFrame from the deployment functions.
    base: str
        The name of the base capacity column in the DataFrame.
    """
    return (df['difference'] / df[base]) * 100


def analyze_algorithm(df, base, proj, ar_dict):
    """
    This function takes in a DataFrame output of the deployment functions
    above, and returns a series of metrics so you can compare different
    deployments.

    Parameters
    ----------
    df: :class:`pandas.DataFrame`
        The output pandas DataFrame from the deployment functions.
    base: str
        The name of the base capacity column in the DataFrame.
    proj: str
        The name of the projected capacity column in the DataFrame.
    ar_dict: dictionary
        A dictionary of reactors with information of the form:
        {reactor: [Power (MWe), capacity_factor (%), lifetime (yr),
        [distribution]]}.

    Returns
    -------
    results: dict
        A dictionary of the results of the analysis.
        above_count: int
            The number of times the deployed capacity exceeds desired capacity.
        below_count: int
            The number of times the deployed capacity is below
            desired capacity.
        equal_count: int
            The number of times the deployed capacity equals desired capacity.
        above_percentage: float
            The percent of times the deployed capacity exceeds
            desired capacity.
        below_percentage: float
            The percent of times the deployed capacity is below desired
            capacity.
        total_above: int
            The excess of deployed capacity.
        total_below: int
            The dearth of deployed capacity.
        percent_provided: dict
            The percent of the deployed capacity that comes from each reactor.
    """

    df['difference'] = df.apply(simple_diff, base=base, proj=proj, axis=1)
    df['percentage'] = df.apply(calc_percentage, base=base, axis=1)

    above_count = (df['difference'] > 0).sum()
    below_count = (df['difference'] < 0).sum()
    equal_count = (df['difference'] == 0).sum()

    above_percentage = (above_count / len(df)) * 100
    below_percentage = (below_count / len(df)) * 100

    total_above = df['difference'][df['difference'] > 0].sum()
    total_below = df['difference'][df['difference'] < 0].sum()

    # Now we will calculate the percent of the total capacity coming from each
    # reactor.
    percent_provided = {}

    total_cap_sum = df['total_cap'].sum()
    for reactor in ar_dict.keys():
        total_reactor_cap = df[f'{reactor}_cap'].sum()
        percent_reactor_cap = (1 -
                               (total_cap_sum - total_reactor_cap) /
                               total_cap_sum) * 100
        percent_provided[reactor] = percent_reactor_cap

    results = {
        'above_count': above_count,
        'below_count': below_count,
        'equal_count': equal_count,
        'above_percentage': above_percentage,
        'below_percentage': below_percentage,
        'total_above': total_above,
        'total_below': total_below,
        'percent_provided': percent_provided
    }

    return results
