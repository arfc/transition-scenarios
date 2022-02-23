import transition_metrics as tm
import unittest
import cymetric
import transition_metrics as tm
import numpy as np
import pandas as pd
import math
from uuid import UUID
from pandas._testing import assert_series_equal
from pandas._testing import assert_frame_equal
import sys
sys.path.insert(0, '../')


class Test_static_info(unittest.TestCase):
    def setUp(self):
        '''
        This defines the output files and a test DataFrame to use within the
        test suite.

        The first output file (transition_metrics_decommission_test.sqlite)
        models Reactor_type1 and Reactor_type2 prototypes with a lifetime of
        2 timesteps. This ensures that all of these prototypes will be
        decommissioned in the simulation.

        The second output file (transition_metrics_nodecommission_test.sqlite)
        models Reactor_type1 and Reactor_type2 prototypes with a lifetime of
        10 timesteps. This ensures that they are not decommissioned during the
        simualtion.

        Both output files model a 7 month fuel cycle with the reactor
        prototypes with manually defined deployment through a
        cycamore::DeployInst. 1 Reactor_type1 is built at timestep 1, 1
        Reactor_type2 is built at both tiemstep 2 and 3.
        '''
        self.output_file1 = 'transition_metrics_decommission_test.sqlite'
        self.output_file2 = 'transition_metrics_nodecommission_test.sqlite'
        self.test_df = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 1, 3], 'Quantity': [
                    2, 5, 6, 8], 'Commodity': [
                    'fresh_uox', 'spent_uox', 'fresh_uox', 'fresh_uox'],
                'Prototype': ['FuelCycle', 'LWR', 'Reactor_type1', 'LWR']})

    def test_get_metrics(self):
        obs = tm.get_metrics(self.output_file1)
        assert isinstance(obs, cymetric.evaluator.Evaluator)

    def test_add_zeros_columns1(self):
        '''
        Tests the add_zeros_columns function when the column names specified
        are in the given dataframe
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 1, 3], 'Quantity': [
                    2, 5, 6, 8], 'Commodity': [
                    'fresh_uox', 'spent_uox', 'fresh_uox', 'fresh_uox'],
                'Prototype': ['FuelCycle', 'LWR', 'Reactor_type1', 'LWR']})
        obs = tm.add_zeros_columns(self.test_df, ['Quantity', 'Time'])
        assert_frame_equal(exp, obs)

    def test_add_zeros_columns2(self):
        '''
        Tests the add_zeros_columns function when the column names specified
        are not in the given dataframe
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 1, 3], 'Quantity': [
                    2, 5, 6, 8], 'Commodity': [
                    'fresh_uox', 'spent_uox', 'fresh_uox', 'fresh_uox'],
                'Prototype': ['FuelCycle', 'LWR', 'Reactor_type1', 'LWR'],
                'reactors': [0.0, 0.0, 0.0, 0.0]
            })
        obs = tm.add_zeros_columns(self.test_df, ['reactors'])
        assert_frame_equal(exp, obs)

    def test_rx_commission_decommission1(self):
        # tests function when facilities are decommissioned
        exp = pd.DataFrame(
            data={'lwr_enter': [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
                  'lwr_exit': [0.0, 0.0, 0.0, 0.0, -1.0, -1.0, 0.0],
                  'lwr_total': [0.0, 0.0, 1.0, 2.0, 1.0, 0.0, 0.0]
                  })
        non_lwr = ['United States', 'FuelCycle', 'FuelSupply',
                   'Repository', 'UNITED_STATES_OF_AMERICA',
                   'Reactor_type1_enter', 'Reactor_type1_exit']
        df = tm.rx_commission_decommission(self.output_file1, non_lwr)
        obs = df[['lwr_enter', 'lwr_exit', 'lwr_total']]
        assert_frame_equal(exp, obs, check_names=False)

    def test_rx_commission_decommission2(self):
        '''
        This tests rx_commission_decommission when the reactors
        are decommissioned and an item in the non_lwr list
        is not an actual prototype in the simulation
        '''
        exp = pd.DataFrame(
            data={'Reactor_type3_enter': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  'lwr_enter': [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
                  'lwr_exit': [0.0, 0.0, 0.0, 0.0, -1.0, -1.0, 0.0],
                  'lwr_total': [0.0, 0.0, 1.0, 2.0, 1.0, 0.0, 0.0]
                  })
        non_lwr = ['United States', 'FuelCycle', 'FuelSupply',
                   'Repository', 'UNITED_STATES_OF_AMERICA',
                   'Reactor_type1', 'Reactor_type3']
        df = tm.rx_commission_decommission(self.output_file1, non_lwr)
        obs = df[['Reactor_type3_enter', 'lwr_enter', 'lwr_exit', 'lwr_total']]
        assert_frame_equal(exp, obs, check_names=False)

    def test_rx_commission_decommission3(self):
        # tests function when facilities are not decommissioned
        exp = pd.DataFrame(data={
            'lwr_enter': [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
            'lwr_exit': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'lwr_total': [0.0, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0]
        })
        non_lwr = ['United States', 'FuelCycle', 'FuelSupply',
                   'Repository', 'UNITED_STATES_OF_AMERICA',
                   'Reactor_type1']
        df = tm.rx_commission_decommission(self.output_file2, non_lwr)
        obs = df[['lwr_enter', 'lwr_exit', 'lwr_total']]
        assert_frame_equal(exp, obs, check_names=False)

    def test_rx_commission_decommission4(self):
        '''
        This tests rx_commission_decommission when the reactors
        are not decommissioned and an item in the non_lwr list
        is not an actual prototype in the simulation
        '''
        exp = pd.DataFrame(
            data={'Reactor_type3_enter': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  'lwr_enter': [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
                  'lwr_exit': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  'lwr_total': [0.0, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0]
                  })
        non_lwr = ['United States', 'FuelCycle', 'FuelSupply',
                   'Repository', 'UNITED_STATES_OF_AMERICA',
                   'Reactor_type1', 'Reactor_type3']
        df = tm.rx_commission_decommission(self.output_file2, non_lwr)
        obs = df[['Reactor_type3_enter', 'lwr_enter', 'lwr_exit', 'lwr_total']]
        assert_frame_equal(exp, obs, check_names=False)

    def test_prototype_totals1(self):
        '''
        The function tests the number of advanced reactors built and the total
        number deployed at the first 4 time steps of
        transition_metrics_decommission_test.sqlite when the Reactor_type1
        and Reactor_type2 are both considered to be advanced reactors.
        In this output, both reactor types are
        '''
        exp = pd.DataFrame(data={
            'advrx_enter': [0.0, 1.0, 1.0, 1.0],
            'advrx_total': [0.0, 1.0, 2.0, 2.0]
        })
        nonlwr = ['Repository', 'FuelSupply', 'United States',
                  'FuelCycle', 'UNITED_STATES_OF_AMERICA']
        obs = tm.prototype_totals(self.output_file1, nonlwr, ['Reactor_type1',
                                                              'Reactor_type2'])
        assert_frame_equal(
            exp, obs[['advrx_enter', 'advrx_total']][0:4], check_names=False)

    def test_prototype_totals2(self):
        '''
        The function tests the number of advanced reactors built and the total
        number deployed at the first 4 time steps of
        transition_metrics_nodecommission_test.sqlite when the Reactor_type1
        and Reactor_type2 are both considered to be advanced reactors.
        In this simulation both reactor types are commissioned, but not
        decommissioned
        '''
        exp = pd.DataFrame(data={
            'advrx_enter': [0.0, 1.0, 1.0, 1.0],
            'advrx_total': [0.0, 1.0, 2.0, 3.0]
        })
        nonlwr = ['Repository', 'FuelSupply', 'United States',
                  'FuelCycle', 'UNITED_STATES_OF_AMERICA']
        obs = tm.prototype_totals(self.output_file2, nonlwr, ['Reactor_type1',
                                                              'Reactor_type2'])
        assert_frame_equal(
            exp, obs[['advrx_enter', 'advrx_total']][0:4], check_names=False)

    def test_add_year(self):
        exp = pd.DataFrame(data={
            'Time': [
                0, 1, 1, 3], 'Quantity': [
                2, 5, 6, 8], 'Commodity': [
                'fresh_uox', 'spent_uox', 'fresh_uox', 'fresh_uox'],
            'Prototype': ['FuelCycle', 'LWR', 'Reactor_type1', 'LWR'],
            'Year': [1965.00, 1965.08, 1965.08, 1965.25]})
        obs = tm.add_year(self.test_df)
        assert_frame_equal(exp, obs)

    def test_get_transactions(self):
        exp = pd.DataFrame(
            data={
                'Time': [
                    0,
                    1,
                    1],
                'SimId': [
                    0,
                    UUID('cf7af291-7fd9-4b27-9cb7-f7af8d9a7269'),
                    UUID('cf7af291-7fd9-4b27-9cb7-f7af8d9a7269')],
                'TransactionId': [
                    0.0,
                    0.0,
                    1.0],
                'ResourceId': [
                    0.0,
                    10.0,
                    12.0],
                'ObjId': [
                    0.0,
                    9.0,
                    10.0],
                'SenderId': [
                    0.0,
                    21.0,
                    21.0],
                'ReceiverId': [
                    0.0,
                    24.0,
                    24.0],
                'Commodity': [
                    0,
                    'fresh_uox',
                    'fresh_uox'],
                'Units': [
                    0,
                    'kg',
                    'kg'],
                'Quantity': [
                    0.0,
                    33000.0,
                    33000.0]})
        obs = tm.get_transactions(self.output_file1)
        assert_frame_equal(exp, obs[0:3])

    def test_sum_and_add_missing_time(self):
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    2.0, 11.0, 0.0, 8.0]})
        obs = tm.sum_and_add_missing_time(self.test_df)
        assert_frame_equal(exp, obs[0:4])

    def test_find_commodity_transactions1(self):
        # tests function when the queried commodity is in the dataframe
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 3], 'Quantity': [
                    2, 6, 8], 'Commodity': [
                        'fresh_uox', 'fresh_uox', 'fresh_uox'], 'Prototype': [
                            'FuelCycle', 'Reactor_type1', 'LWR']}).set_index(
                                [
                                    pd.Index(
                                        [
                                            0, 2, 3])])
        obs = tm.find_commodity_transactions(self.test_df, 'fresh_uox')
        assert_frame_equal(exp, obs)

    def test_find_commodity_transactions2(self):
        # tests function when the queried commodity is not in the dataframe
        exp = pd.DataFrame(data={'Time': [], 'Quantity': [],
                                 'Commodity': [], 'Prototype': []})
        obs = tm.find_commodity_transactions(self.test_df, 'tails')
        assert_frame_equal(exp, obs, check_dtype=False)

    def test_find_prototype_transactions1(self):
        # tests function when the queried prototype is in the dataframe
        exp = pd.DataFrame(data={'Time': [1, 3],
                                 'Quantity': [5, 8],
                                 'Commodity': ['spent_uox', 'fresh_uox'],
                                 'Prototype': ['LWR', 'LWR']}
                           ).set_index([pd.Index([1, 3])])
        obs = tm.find_prototype_transactions(self.test_df, 'LWR')
        assert_frame_equal(exp, obs)

    def test_find_prototype_transactions2(self):
        # tests function when the queried prototype is not in the dataframe
        exp = pd.DataFrame(data={'Time': [], 'Quantity': [], 'Commodity':
                                 [], 'Prototype': []})
        obs = tm.find_prototype_transactions(self.test_df, 'Reactor_type2')
        assert_frame_equal(exp, obs, check_dtype=False)

    def test_commidity_mass_traded1(self):
        # tests function when the queried commodity is in the dataframe
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    2.0, 6.0, 0.0, 8.0], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        obs = tm.commodity_mass_traded(self.test_df, 'fresh_uox')
        assert_frame_equal(exp, obs[0:4])

    def test_commidity_mass_traded2(self):
        # tests function when the queried commodity is not in the dataframe
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 0.0, 0.0], 'Year': [
                        1965.0, 1965.08, 1965.17, 1965.25]})
        obs = tm.commodity_mass_traded(self.test_df, 'tails')
        assert_frame_equal(exp, obs[0:4])

    def test_add_receiver_prototype(self):
        exp = pd.DataFrame(
            data={
                'Time': [
                    1,
                    1,
                    1,
                    2],
                'SimId': [
                    UUID('cf7af291-7fd9-4b27-9cb7-f7af8d9a7269'),
                    UUID('cf7af291-7fd9-4b27-9cb7-f7af8d9a7269'),
                    UUID('cf7af291-7fd9-4b27-9cb7-f7af8d9a7269'),
                    UUID('cf7af291-7fd9-4b27-9cb7-f7af8d9a7269')],
                'TransactionId': [
                    0.0,
                    1.0,
                    2.0,
                    3.0],
                'ResourceId': [
                    10.0,
                    12.0,
                    14.0,
                    15.0],
                'ObjId': [
                    9.0,
                    10.0,
                    11.0,
                    9.0],
                'SenderId': [
                    21.0,
                    21.0,
                    21.0,
                    24.0],
                'ReceiverId': [
                    24.0,
                    24.0,
                    24.0,
                    22.0],
                'Commodity': [
                    'fresh_uox',
                    'fresh_uox',
                    'fresh_uox',
                    'spent_uox'],
                'Units': [
                    'kg',
                    'kg',
                    'kg',
                    'kg'],
                'Quantity': [
                    33000.0,
                    33000.0,
                    33000.0,
                    33000.0],
                'Prototype': [
                    'Reactor_type1',
                    'Reactor_type1',
                    'Reactor_type1',
                    'Repository']})
        obs = tm.add_receiver_prototype(self.output_file1)
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_to_prototype1(self):
        # tests function when the queried commodity and prototype are in the
        # dataframe
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 9900.00, 13200.00], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        transactions_df = tm.add_receiver_prototype(self.output_file1)
        obs = tm.commodity_to_prototype(
            transactions_df, 'fresh_uox', 'Reactor_type2')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_to_prototype2(self):
        # tests function when the queried commodity is not in the dataframe
        # but the prototype is
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 0.0, 0.0], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        transactions_df = tm.add_receiver_prototype(self.output_file1)
        obs = tm.commodity_to_prototype(
            transactions_df, 'fresh_uox', 'Reactor_type3')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_to_prototype3(self):
        # tests function when the queried commodity is in the dataframe
        # but the prototype is not
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 0.0, 0.0], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        transactions_df = tm.add_receiver_prototype(self.output_file1)
        obs = tm.commodity_to_prototype(
            transactions_df, 'tails', 'Reactor_type2')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_to_prototype4(self):
        # tests function when the queried commodity and prototype are not
        # in the dataframe
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 0.0, 0.0], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        transactions_df = tm.add_receiver_prototype(self.output_file1)
        obs = tm.commodity_to_prototype(
            transactions_df, 'tails', 'Reactor_type3')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_to_LWR1(self):
        '''
        This function tests the transactions returned when the
        commodity specified (fresh_uox) is used in the simulation and the
        prototype specified (Reactor_type2) is in the simulation and receives
        the commodity specified.
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 99000.0, 33000.0, 0.0], 'Year': [
                    1965.00, 1965.08, 1965.17, 1965.25]})
        transactions_df = tm.add_receiver_prototype(self.output_file1)
        obs = tm.commodity_to_LWR(
            transactions_df,
            'fresh_uox',
            'Reactor_type2')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_to_LWR2(self):
        '''
        This function tests the transactions returned when the
        commodity specified (fresh_uox) is used in the simulation and the
        prototype specified (Repository) is not in the simulation and does not
        receive the commodity specified.
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 99000.0, 42900.0, 13200.0], 'Year': [
                    1965.00, 1965.08, 1965.17, 1965.25]})
        transactions_df = tm.add_receiver_prototype(self.output_file1)
        obs = tm.commodity_to_LWR(transactions_df, 'fresh_uox', 'Repository')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_to_LWR3(self):
        '''
        This function tests the transactions returned when the
        commodity specified (u_ore) is not used in the simulation and the
        prototype specified (Reactor_type2) is in the simulation.
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 0.0, 0.0], 'Year': [
                    1965.00, 1965.08, 1965.17, 1965.25]})
        transactions_df = tm.add_receiver_prototype(self.output_file1)
        obs = tm.commodity_to_LWR(transactions_df, 'u_ore', 'Reactor_type2')
        assert_frame_equal(exp, obs[0:4])

    def test_get_annual_electricity(self):
        exp = pd.DataFrame(data={'Year': [1965], 'Energy': [0.120]})
        obs = tm.get_annual_electricity(self.output_file1)
        assert_frame_equal(exp, obs)

    def test_get_prototype_energy1(self):
        # tests function when the queried prototype is in the dataframe
        exp = pd.DataFrame(data={'Year': [1965, 1966], 'Energy': [0.02, 0.00]})
        obs = tm.get_prototype_energy(self.output_file1, 'Reactor_type2')
        assert_frame_equal(exp, obs[0:2])

    def test_get_prototype_energy2(self):
        # tests function when the queried prototype is not in the dataframe
        exp = pd.DataFrame(data={'Year': [1965, 1966], 'Energy': [0.00, 0.00]})
        obs = tm.get_prototype_energy(self.output_file1, 'Reactor_type3')
        assert_frame_equal(exp, obs[0:2])

    def test_get_lwr_energy1(self):
        # tests function when the queried non-LWR prototype is in the dataframe
        exp = pd.DataFrame(data={'Year': [1965, 1966], 'Energy': [0.10, 0.00]})
        obs = tm.get_lwr_energy(self.output_file1, 'Reactor_type2')
        assert_frame_equal(exp, obs[0:2])

    def test_get_lwr_energy2(self):
        # tests function when the queried non-LWR prototype is not in the
        # dataframe
        exp = pd.DataFrame(data={'Year': [1965, 1966], 'Energy': [0.12, 0.00]})
        obs = tm.get_lwr_energy(self.output_file1, 'Reactor_type3')
        assert_frame_equal(exp, obs[0:2])


def test_separation_potential1():
    # tests value between 0 and 1
    exp = 0.8317766166719346
    obs = tm.separation_potential(0.8)
    assert exp == obs


def test_separation_potential2():
    # tests value greater than 1
    obs = tm.separation_potential(1.2)
    assert math.isnan(obs)


def test_separation_potential3():
    # tests value less than 0
    obs = tm.separation_potential(-1.2)
    assert math.isnan(obs)


def test_separation_potential4():
    # tests use of a DataFrame and 0 as an input
    exp = pd.Series(data=[float('inf'), 1.757780, 0.831777])
    data = pd.Series(data=[0.0, 0.1, 0.2])
    obs = tm.separation_potential(data)
    assert_series_equal(exp, obs)


def test_calculate_SWU1():
    # tests floats as inputs
    exp = 45.16041363237984
    obs = tm.calculate_SWU(100, 0.4, 50, 0.1, 150, 0.3)
    assert exp == obs


def test_calculate_SWU2():
    # tests DataFrame as an input
    exp = pd.Series(data=[45.16041363237984, 9.032082726475968])
    data = pd.DataFrame(data={'Product': [100, 20], 'Tails': [50, 10],
                              'Feed': [150, 30]})
    obs = tm.calculate_SWU(data['Product'], 0.4, data['Tails'], 0.1,
                           data['Feed'], 0.3)
    assert_series_equal(exp, obs)


def test_calculate_tails1():
    # tests floats as the inputs
    exp = 50.00000000000002
    obs = tm.calculate_tails(100, 0.4, 0.1, 0.3)
    assert exp == obs


def test_calculate_tails2():
    # tests a Series as the input
    exp = pd.Series(data=[50.00000000000002, 10.000000000000005])
    data = pd.Series(data=[100, 20])
    obs = tm.calculate_tails(data, 0.4, 0.1, 0.3)
    assert_series_equal(exp, obs)


def test_calculate_feed1():
    # tests integers as the inputs
    exp = 10
    product = 5
    tails = 5
    obs = tm.calculate_feed(product, tails)
    assert exp == obs


def test_calculate_feed2():
    # tests a DataFrame as the input
    exp = pd.Series(data=[10, 10, 10, 10])
    product = pd.DataFrame(
        data={
            'a': [
                5, 5, 5, 5], 'b': [
                4, 4, 4, 4]}, columns={
                    'a', 'b'})
    tails = pd.DataFrame(
        data={
            'a': [
                5, 5, 5, 5], 'b': [
                4, 4, 4, 4]}, columns={
                    'a', 'b'})
    obs = tm.calculate_feed(product['a'], tails['a'])
    assert np.all(exp == obs)
