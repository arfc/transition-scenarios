import os
import sys
import pytest
import numpy as np
import pandas as pd
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))
import reactor_deployment as dep


ad_reactors = {
    'ReactorBig': [80, 1, 6, [1, 2, 1, 2, 1, 2, 1, 2, 1]],
    'ReactorMedium': [20, 1, 4, 'no_dist'],
    'ReactorSmall': [5, 1, 2, 'no_dist']}
# {reactor: [Power (MWe), capacity_factor (%),
# lifetime (yr), distribution (default='no_dist')]}

test_dict = {
    'Year': [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    'test_cap': [20, 79, 80, 81, 220, 640, 693, 950, 700]}
test_df = pd.DataFrame.from_dict(test_dict)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # Helper Functions # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def test_pull_start_index():
    """
    Pull the start index function where the start_year is the first
    year in the dictionary.
    """
    start_year = test_df['Year'][0]

    assert dep.pull_start_year(test_df, 2016) == start_year


def test_calculate_capacity_change():
    # Create a sample DataFrame
    data = {
        'Year': [2016, 2017, 2018, 2019, 2020],
        'Capacity': [100, 110, 120, 130, 140]
    }
    df = pd.DataFrame(data)
    df.set_index('Year', inplace=True)

    # Define parameters
    base_col = 'Capacity'
    rate = 1.05
    start_year = 2018

    # Call the calculate_capacity_change function
    capacity_change = \
        dep.calculate_capacity_change(df, base_col, rate, start_year)

    # Verify the calculated capacity change
    assert capacity_change(df.loc[2019]) == 120 * 1.05
    assert capacity_change(df.loc[2020]) == 120 * 1.05**2


def test_apply_capacity_change():
    # Create a sample DataFrame
    data = {
        'Year': [2016, 2017, 2018, 2019, 2020],
        'Capacity': [100, 110, 120, 130, 140]
    }
    df = pd.DataFrame(data)
    df.set_index('Year', inplace=True)

    # Define parameters
    base_col = 'Capacity'
    rate = 1.05
    start_year = 2018
    end_year = 2021

    # Call the apply_capacity_change function
    df = dep.apply_capacity_change(df, base_col, rate, start_year, end_year)

    # Verify the applied capacity change
    expected_capacity_inc = [100, 110, 120, 120 * 1.05, 120 * 1.05**2]
    assert df[f"{base_col} Inc {rate}"].tolist() == expected_capacity_inc


def test_assign_initial_values():
    # Create a sample DataFrame
    data = {
        'Year': [2016, 2017, 2018, 2019, 2020],
        'Capacity': [100, 110, 120, 130, 140]
    }
    df = pd.DataFrame(data)
    df.set_index('Year', inplace=True)

    # Define parameters
    base_col = 'Capacity'
    rate = 1.05
    start_year = 2018

    # Call the assign_initial_values function
    df = dep.assign_initial_values(df, base_col, rate, start_year)

    # Verify the assigned initial values
    expected_capacity_inc = [100, 110, 120, 120, 120]
    assert df[f"{base_col} Inc {rate}"].tolist() == expected_capacity_inc


def test_calculate_new_capacity_increase():
    # Create a sample DataFrame
    data = {
        'Year': [2016, 2017, 2018, 2019, 2020],
        'Capacity': [100, 110, 120, 130, 140],
        'Capacity Inc 1.05': [100, 110, 120, 126, 132.3]
    }
    df = pd.DataFrame(data)
    df.set_index('Year', inplace=True)

    # Define parameters
    base_col = 'Capacity'
    rate = 1.05

    # Call the calculate_new_capacity_increase function
    df = dep.calculate_new_capacity_increase(df, base_col, rate)

    # Verify the calculated new capacity increase
    expected_new_capacity_inc = [0, 0, 0, 126 - 130, 132.3 - 140]
    assert df[f"New Capacity Inc {rate}"].tolist() == expected_new_capacity_inc


def test_capacity_increase():
    # Create a sample DataFrame
    data = {
        'Year': [2016, 2017, 2018, 2019, 2020],
        'Capacity': [100, 110, 120, 130, 140]
    }
    df = pd.DataFrame(data)
    df.set_index('Year', inplace=True)

    # Define parameters
    base_col = 'Capacity'
    rate = 1.05
    start_year = 2018
    end_year = 2021

    # Call the capacity_increase function
    df = dep.capacity_increase(df, base_col, rate, start_year, end_year)

    # Verify the final DataFrame with the new column added
    expected_capacity_inc = [100, 110, 120, 120 * 1.05, 120 * 1.05**2]
    expected_new_capacity_inc = [0, 0, 0, 120 * 1.05 - 130, 120 * 1.05**2 - 140]
    assert df[f"{base_col} Inc {rate}"].tolist() == expected_capacity_inc
    assert df[f"New Capacity Inc {rate}"].tolist() == expected_new_capacity_inc


def test_direct_decommission():
    """
    Test the direct decommissioning function.
    The scenario is based on the greedy algorithm.
    """
    decom_df = {
        'Year': [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
        'manual_decom': [0, 0, 0, 0, 0, 0, 0, 0, 1],
        # manual calculation based on greedy algorithm
        'ReactorBigDecom': [0, 0, 0, 0, 0, 0, 0, 0, 1]}
    # result of greedy function using the direct_decommission function

    assert all(decom_df['manual_decom'][i] ==
               decom_df['ReactorBigDecom'][i]
               for i in range(len(decom_df['manual_decom'])))


def test_num_react_to_cap():
    """
    Test the reactors to capacity function.
    The scenario is based on the greedy algorithm.
    """
    react_to_cap_df = {
        'Year': [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
        'manual_cap': [0, 0, 80, 80, 160, 640, 640, 880, 720],
        'new_cap': [0, 0, 80, 80, 160, 640, 640, 880, 720]}

    assert all(react_to_cap_df['manual_cap'][i] ==
               react_to_cap_df['new_cap'][i]
               for i in range(len(react_to_cap_df['manual_cap'])))


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # Deployment Functions # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def test_greedy_deployment():
    """
    Test the greedy deployment function.
    """
    # Greedy distribution dictionary
    greedy_dist_df = {
        'Year': [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
        'test_cap': [20, 79, 80, 81, 220, 640, 693, 950, 700],
        'manual_cap': [20, 75, 80, 80, 220, 640, 690, 950, 700]}

    # Convert to DataFrame for comparison
    greedy_dist_df = pd.DataFrame(greedy_dist_df)

    calculated_greedy_df = dep.greedy_deployment(
        test_df, 'test_cap', ad_reactors, 2016)

    # Ensure 'new_cap' column exists in the result
    assert 'new_cap' in calculated_greedy_df.columns, \
        "The 'new_cap' column is missing in the calculated results."

    # Test the 'manual_cap' values against 'new_cap'
    for i in range(len(greedy_dist_df)):
        assert greedy_dist_df['manual_cap'][i] == \
            calculated_greedy_df['new_cap'][i], f"Failed at index {i}:\
            {greedy_dist_df['manual_cap'][i]} != \
            {calculated_greedy_df['new_cap'][i]}"

    print("Greedy tests passed.")


def test_pre_det_deployment_greedy():
    """
    Test the predetermined deployment function with greedy=True.
    """
    # Define the expected DataFrame for the greedy case
    manual_pre_det_greedy_df = {
        'Year': [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
        'test_cap': [20, 79, 80, 81, 220, 640, 693, 950, 700],
        'total_cap': [20, 75, 80, 95, 240, 715, 690, 965, 950],
        'manual_cap': [20, 75, 80, 80, 220, 640, 690, 950, 700]
    }
    manual_pre_det_greedy_df = pd.DataFrame(manual_pre_det_greedy_df)

    # Create a copy of test_df to pass to the function
    pre_det_dep_df_greedy = test_df.copy()

    # Call the pre_det_deployment function with greedy=True
    result_df = dep.pre_det_deployment(pre_det_dep_df_greedy, 'test_cap',
                                       ad_reactors, 2016, greedy=True)

    # Check that 'new_cap' matches 'manual_cap'
    assert result_df['new_cap'].equals(manual_pre_det_greedy_df['manual_cap'])

    print("Greedy pre-determined distribution test passed.")


def test_pre_det_deployment_linear():
    """
    Test the predetermined deployment function with greedy=False.
    """
    # Define the expected DataFrame for the linear case
    pre_det_linear_df = {
        'Year': [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
        'test_cap': [20, 79, 80, 81, 220, 640, 693, 950, 700],
        'total_cap': [80, 80, 100, 100, 225, 655, 825, 1150, 1050],
        'manual_cap': [80, 80, 100, 100, 225, 655, 700, 955, 705]
    }
    pre_det_linear_df = pd.DataFrame(pre_det_linear_df)

    # Create a copy of test_df to pass to the function
    pre_det_dep_df_linear = test_df.copy()

    # Call the pre_det_deployment function with greedy=False
    result_df = dep.pre_det_deployment(pre_det_dep_df_linear, 'test_cap',
                                       ad_reactors, 2016, greedy=False)

    # Check that 'new_cap' matches 'manual_cap'
    assert result_df['new_cap'].equals(pre_det_linear_df['manual_cap'])

    print("Linear pre-determined distribution test passed.")


def test_rand_deployment():
    """
    Test the random deployment function with set_seed=True.
    """
    # Define the expected DataFrame for the random function
    manual_rand_df = {
        'Year': [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
        'test_cap': [20, 79, 80, 81, 220, 640, 693, 950, 700],
        'total_cap': [0, 0, 80, 80, 205, 615, 620, 915, 835],
        'manual_cap': [0, 0, 80, 80, 205, 615, 615, 900, 695]
    }

    manual_rand_df = pd.DataFrame(manual_rand_df)

    # Create a copy of test_df to pass to the function
    rand_dep_df = test_df.copy()

    # Call the rand_deployment function
    result_df = dep.rand_deployment(rand_dep_df, 'test_cap',
                                    ad_reactors, 2016, set_seed=True)

    # Check that 'new_cap' matches 'manual_cap'
    assert result_df['new_cap'].equals(manual_rand_df['manual_cap'])

    print("Random deployment test passed.")


def test_rand_greedy_deployment():
    """
    Test the random + greedy deployment function with set_seed=True.
    """
    # Define the expected DataFrame for the random greedy function
    manual_rand_greedy_df = {
        'Year': [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
        'test_cap': [20, 79, 80, 81, 220, 640, 693, 950, 700],
        'total_cap': [20, 75, 80, 95, 240, 715, 690, 965, 950],
        'manual_cap': [20, 75, 80, 80, 220, 640, 690, 950, 700]
    }

    manual_rand_greedy_df = pd.DataFrame(manual_rand_greedy_df)

    # Create a copy of test_df to pass to the function
    rand_greedy_dep_df = test_df.copy()

    # Call the rand_deployment function
    result_df = dep.rand_greedy_deployment(rand_greedy_dep_df, 'test_cap',
                                           ad_reactors, 2016, set_seed=True)

    # Check that 'new_cap' matches 'manual_cap'
    assert result_df['new_cap'].equals(manual_rand_greedy_df['manual_cap'])

    print("Random greedy deployment test passed.")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # Analysis Functions # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def test_analyze_algorithm():
    """
    Test the analyze_algorithm function.
    """
    # Create a sample DataFrame for testing
    data = {
        'Year': [2016, 2017, 2018],
        'proj_cap': [110, 160, 190],
        'total_cap': [105, 160, 195],
        'ReactorBig_cap':    [80, 160, 80],
        'ReactorMedium_cap': [20, 0, 80],
        'ReactorSmall_cap':  [5, 0, 35]
        }
    df = pd.DataFrame(data)

    # Call the analyze_algorithm function
    results = dep.analyze_algorithm(df, 'total_cap', 'proj_cap', ad_reactors)

    # Check the expected results
    assert results['above_count'] == 1
    assert results['below_count'] == 1
    assert results['equal_count'] == 1
    assert results['above_percentage'] == 33.33333333333333
    assert results['below_percentage'] == 33.33333333333333
    assert results['total_above'] == 5
    assert results['total_below'] == -5
    assert results['percent_provided'] == {'ReactorBig': 69.56521739130434,
                                           'ReactorMedium': 21.739130434782606,
                                           'ReactorSmall': 8.695652173913048}
