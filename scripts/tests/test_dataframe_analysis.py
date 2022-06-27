import unittest
import numpy as np
import pandas as pd
import math
from pandas._testing import assert_frame_equal
from pandas._testing import assert_series_equal
import sys

sys.path.insert(0, '../')
import dataframe_analysis as dfa


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

        Both output files model a 7-month fuel cycle for reactor
        prototypes with manually defined deployment through a
        cycamore::DeployInst. 1 Reactor_type1 is built at timestep 1, and 1
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
                'ReceiverPrototype': ['FuelCycle', 'LWR', 'Reactor_type1', 'LWR'],
                'SenderPrototype': ['UnitedStates', 'LWR', 'FuelCycle', 'Reactor_type1']
            })

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
                'ReceiverPrototype': ['FuelCycle', 'LWR', 'Reactor_type1', 'LWR'],
                'SenderPrototype': ['UnitedStates', 'LWR', 'FuelCycle', 'Reactor_type1']})
        obs = dfa.add_zeros_columns(self.test_df, ['Quantity', 'Time'])
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
                'ReceiverPrototype': ['FuelCycle', 'LWR', 'Reactor_type1', 'LWR'],
                'SenderPrototype': ['UnitedStates', 'LWR', 'FuelCycle', 'Reactor_type1'],
                'reactors': [0.0, 0.0, 0.0, 0.0]
            })
        obs = dfa.add_zeros_columns(self.test_df, ['reactors'])
        assert_frame_equal(exp, obs)

    def test_add_year(self):
        exp = pd.DataFrame(data={
            'Time': [
                0, 1, 1, 3], 'Quantity': [
                2, 5, 6, 8], 'Commodity': [
                'fresh_uox', 'spent_uox', 'fresh_uox', 'fresh_uox'],
            'ReceiverPrototype': ['FuelCycle', 'LWR', 'Reactor_type1', 'LWR'],
            'SenderPrototype': ['UnitedStates', 'LWR', 'FuelCycle', 'Reactor_type1'],
            'Year': [1965.00, 1965.08, 1965.08, 1965.25]})
        obs = dfa.add_year(self.test_df)
        assert_frame_equal(exp, obs)

    def test_sum_and_add_missing_time(self):
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    2.0, 11.0, 0.0, 8.0]})
        obs = dfa.sum_and_add_missing_time(self.test_df)
        assert_frame_equal(exp, obs[0:4])

    def test_find_commodity_transactions1(self):
        '''
        Tests function when the queried commodity is in the dataframe
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 3], 'Quantity': [
                    2, 6, 8], 'Commodity': [
                        'fresh_uox', 'fresh_uox', 'fresh_uox'],
                'ReceiverPrototype': [
                    'FuelCycle', 'Reactor_type1', 'LWR'],
                'SenderPrototype': ['UnitedStates', 'FuelCycle', 'Reactor_type1']}).set_index(
            [
                pd.Index(
                    [
                        0, 2, 3])])
        obs = dfa.find_commodity_transactions(self.test_df, 'fresh_uox')
        assert_frame_equal(exp, obs)

    def test_find_commodity_transactions2(self):
        '''
        Tests function when the queried commodity is not in the dataframe
        '''
        exp = pd.DataFrame(data={'Time': [], 'Quantity': [],
                                 'Commodity': [], 'ReceiverPrototype': [],
                                 'SenderPrototype': []})
        obs = dfa.find_commodity_transactions(self.test_df, 'tails')
        assert_frame_equal(exp, obs, check_dtype=False)

    def test_find_prototype_receiver1(self):
        '''
        Tests function when the queried prototype is in the dataframe
        '''
        exp = pd.DataFrame(data={'Time': [1, 3],
                                 'Quantity': [5, 8],
                                 'Commodity': ['spent_uox', 'fresh_uox'],
                                 'ReceiverPrototype': ['LWR', 'LWR'],
                                 'SenderPrototype': ['LWR', 'Reactor_type1']}
                           ).set_index([pd.Index([1, 3])])
        obs = dfa.find_prototype_receiver(self.test_df, 'LWR')
        assert_frame_equal(exp, obs)

    def test_find_prototype_receiver2(self):
        ''''
        Tests function when the queried prototype is not in the dataframe
        '''
        exp = pd.DataFrame(data={'Time': [], 'Quantity': [], 'Commodity':
                                 [], 'ReceiverPrototype': [],
                                 'SenderPrototype': []})
        obs = dfa.find_prototype_receiver(self.test_df, 'Reactor_type2')
        assert_frame_equal(exp, obs, check_dtype=False)

    def test_find_prototype_sender1(self):
        '''
        Tests function when the queried prototype is in the dataframe
        '''
        exp = pd.DataFrame(data={'Time': [1],
                                 'Quantity': [5],
                                 'Commodity': ['spent_uox'],
                                 'ReceiverPrototype': ['LWR'],
                                 'SenderPrototype': ['LWR']}
                           ).set_index([pd.Index([1])])
        obs = dfa.find_prototype_sender(self.test_df, 'LWR')
        assert_frame_equal(exp, obs)

    def test_find_prototype_sender2(self):
        ''''
        Tests function when the queried prototype is not in the dataframe
        '''
        exp = pd.DataFrame(data={'Time': [], 'Quantity': [], 'Commodity':
                                 [], 'ReceiverPrototype': [],
                                 'SenderPrototype': []})
        obs = dfa.find_prototype_sender(self.test_df, 'Reactor_type2')
        assert_frame_equal(exp, obs, check_dtype=False)

    def test_commidity_mass_traded1(self):
        '''
        Tests function when the queried commodity is in the dataframe
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    2.0, 6.0, 0.0, 8.0], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        obs = dfa.commodity_mass_traded(self.test_df, 'fresh_uox')
        assert_frame_equal(exp, obs[0:4])

    def test_commidity_mass_traded2(self):
        '''
        Tests function when the queried commodity is not in the dataframe
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 0.0, 0.0], 'Year': [
                        1965.0, 1965.08, 1965.17, 1965.25]})
        obs = dfa.commodity_mass_traded(self.test_df, 'tails')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_to_prototype1(self):
        '''
        Tests function when the queried commodity and prototype are in the
        dataframe
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 6.0, 0.0, 0.0], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        obs = dfa.commodity_to_prototype(
            self.test_df, 'fresh_uox', 'Reactor_type1')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_to_prototype2(self):
        '''
        Tests function when the queried commodity is not in the dataframe
        but the prototype is
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 0.0, 0.0], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        obs = dfa.commodity_to_prototype(
            self.test_df, 'fresh_uox', 'Reactor_type3')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_to_prototype3(self):
        '''
        Tests function when the queried commodity is in the dataframe
        but the prototype is not
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 0.0, 0.0], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        obs = dfa.commodity_to_prototype(
            self.test_df, 'tails', 'Reactor_type2')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_to_prototype4(self):
        '''
        Tests function when the queried commodity and prototype are not
        in the dataframe
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 0.0, 0.0], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        obs = dfa.commodity_to_prototype(
            self.test_df, 'tails', 'Reactor_type3')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_from_prototype1(self):
        '''
        Tests function when the queried commodity and prototype are
        in the dataframe
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 0.0, 8.0], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        obs = dfa.commodity_from_prototype(
            self.test_df, 'fresh_uox', 'Reactor_type1')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_from_prototype2(self):
        '''
        Tests function when the queried commodity is not in the dataframe
        but the prototype is
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 0.0, 0.0], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        obs = dfa.commodity_from_prototype(
            self.test_df, 'fresh_uox', 'Reactor_type3')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_from_prototype3(self):
        '''
        Tests function when the queried commodity is in the dataframe
        but the prototype is not
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 0.0, 0.0], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        obs = dfa.commodity_from_prototype(
            self.test_df, 'tails', 'Reactor_type2')
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_from_prototype4(self):
        '''
        Tests function when the queried commodity and prototype are not
        in the dataframe
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    0.0, 0.0, 0.0, 0.0], 'Year': [
                        1965.00, 1965.08, 1965.17, 1965.25]})
        obs = dfa.commodity_from_prototype(
            self.test_df, 'tails', 'Reactor_type3')
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
                    2.0, 0.0, 0.0, 8.0], 'Year': [
                    1965.00, 1965.08, 1965.17, 1965.25]})
        obs = dfa.commodity_to_LWR(
            self.test_df,
            'fresh_uox',
            ['Reactor_type1'])
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
                    2.0, 6.0, 0.0, 8.0], 'Year': [
                    1965.00, 1965.08, 1965.17, 1965.25]})
        obs = dfa.commodity_to_LWR(self.test_df, 'fresh_uox', ['Repository'])
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
        obs = dfa.commodity_to_LWR(self.test_df, 'u_ore', ['Reactor_type2'])
        assert_frame_equal(exp, obs[0:4])

    def test_commodity_to_LWR4(self):
        '''
        This function tests the transactions returned when there are
        multiple prototypes specified in the inputs (Reactor_type2,
        Repository), given as a list. The commodity specified is
        present in the simulation, and sent to one of the specified
        prototypes (Reactor_type2), but not the other (Repository).
        '''
        exp = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 2, 3], 'Quantity': [
                    2.0, 6.0, 0.0, 8.0], 'Year': [
                    1965.00, 1965.08, 1965.17, 1965.25]})
        obs = dfa.commodity_to_LWR(self.test_df, 'fresh_uox',
                                   ['Reactor_type2', 'Repository'])
        assert_frame_equal(exp, obs[0:4])


def test_separation_potential1():
    '''
    Tests value between 0 and 1
    '''
    exp = 0.8317766166719346
    obs = dfa.separation_potential(0.8)
    assert exp == obs


def test_separation_potential2():
    '''
    Tests value greater than 1
    '''
    obs = dfa.separation_potential(1.2)
    assert math.isnan(obs)


def test_separation_potential3():
    '''
    Tests value less than 0
    '''
    obs = dfa.separation_potential(-1.2)
    assert math.isnan(obs)


def test_separation_potential4():
    '''
    Tests use of a DataFrame and 0 as an input
    '''
    exp = pd.Series(data=[float('inf'), 1.757780, 0.831777])
    data = pd.Series(data=[0.0, 0.1, 0.2])
    obs = dfa.separation_potential(data)
    assert_series_equal(exp, obs)


def test_calculate_SWU1():
    '''
    Tests floats as inputs
    '''
    exp = 45.16041363237984
    obs = dfa.calculate_SWU(100, 0.4, 50, 0.1, 150, 0.3)
    assert exp == obs


def test_calculate_SWU2():
    '''
    Tests DataFrame as an input
    '''
    exp = pd.Series(data=[45.16041363237984, 9.032082726475968])
    data = pd.DataFrame(data={'Product': [100, 20], 'Tails': [50, 10],
                              'Feed': [150, 30]})
    obs = dfa.calculate_SWU(data['Product'], 0.4, data['Tails'], 0.1,
                            data['Feed'], 0.3)
    assert_series_equal(exp, obs)


def test_calculate_tails1():
    '''
    Tests floats as the inputs
    '''
    exp = 50.00000000000002
    obs = dfa.calculate_tails(100, 0.4, 0.1, 0.3)
    assert exp == obs


def test_calculate_tails2():
    '''
    Tests a Series as the input
    '''
    exp = pd.Series(data=[50.00000000000002, 10.000000000000005])
    data = pd.Series(data=[100, 20])
    obs = dfa.calculate_tails(data, 0.4, 0.1, 0.3)
    assert_series_equal(exp, obs)


def test_calculate_feed1():
    '''
    Tests integers as the inputs
    '''
    exp = 10
    product = 5
    tails = 5
    obs = dfa.calculate_feed(product, tails)
    assert exp == obs


def test_calculate_feed2():
    '''
    Tests a DataFrame as the input
    '''
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
    obs = dfa.calculate_feed(product['a'], tails['a'])
    assert np.all(exp == obs)
