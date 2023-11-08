import unittest
import cymetric
import numpy as np
import pandas as pd
import math
from uuid import UUID
from pandas._testing import assert_series_equal
from pandas._testing import assert_frame_equal
import sys

sys.path.insert(0, '../')
import transition_metrics as tm


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

    def test_get_lwr_totals1(self):
        '''
        This tests get_lwr_totals when the reactors
        are decommissioned and all items in the non_lwr list
        are actual prototypes in the simulation
        '''
        exp = pd.DataFrame(
            data={'lwr_enter': [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
                  'lwr_exit': [0.0, 0.0, 0.0, 0.0, -1.0, -1.0, 0.0],
                  'lwr_total': [0.0, 0.0, 1.0, 2.0, 1.0, 0.0, 0.0]
                  })
        non_lwr = ['United States', 'FuelCycle', 'FuelSupply',
                   'Repository', 'UNITED_STATES_OF_AMERICA',
                   'Reactor_type1', 'Reactor_type1']
        df = tm.get_lwr_totals(self.output_file1, non_lwr)
        obs = df[['lwr_enter', 'lwr_exit', 'lwr_total']]
        assert_frame_equal(exp, obs, check_names=False)

    def test_get_lwr_totals2(self):
        '''
        This tests get_lwr_totals when the reactors
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
        df = tm.get_lwr_totals(self.output_file1, non_lwr)
        obs = df[['Reactor_type3_enter', 'lwr_enter', 'lwr_exit', 'lwr_total']]
        assert_frame_equal(exp, obs, check_names=False)

    def test_get_lwr_totals3(self):
        '''
        This tests get_lwr_totals when the reactors
        are not decommissioned and all items in the non_lwr list
        are actual prototypes in the simulation
        '''
        exp = pd.DataFrame(data={
            'lwr_enter': [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
            'lwr_exit': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'lwr_total': [0.0, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0]
        })
        non_lwr = ['United States', 'FuelCycle', 'FuelSupply',
                   'Repository', 'UNITED_STATES_OF_AMERICA',
                   'Reactor_type1']
        df = tm.get_lwr_totals(self.output_file2, non_lwr)
        obs = df[['lwr_enter', 'lwr_exit', 'lwr_total']]
        assert_frame_equal(exp, obs, check_names=False)

    def test_get_lwr_totals4(self):
        '''
        This tests get_lwr_totals when the reactors
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
        df = tm.get_lwr_totals(self.output_file2, non_lwr)
        obs = df[['Reactor_type3_enter', 'lwr_enter', 'lwr_exit', 'lwr_total']]
        assert_frame_equal(exp, obs, check_names=False)

    def test_get_prototype_totals1(self):
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
        obs = tm.get_prototype_totals(
            self.output_file1, nonlwr, [
                'Reactor_type1', 'Reactor_type2'])
        assert_frame_equal(
            exp, obs[['advrx_enter', 'advrx_total']][0:4], check_names=False)

    def test_get_prototype_totals2(self):
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
        obs = tm.get_prototype_totals(
            self.output_file2, nonlwr, [
                'Reactor_type1', 'Reactor_type2'])
        assert_frame_equal(
            exp, obs[['advrx_enter', 'advrx_total']][0:4], check_names=False)

    def test_add_receiver_prototype(self):
        exp = pd.DataFrame(
            data={
                'SimId': [
                    UUID('17b1bed5-0981-4682-a9be-05e60e7257cc'),
                    UUID('17b1bed5-0981-4682-a9be-05e60e7257cc'),
                    UUID('17b1bed5-0981-4682-a9be-05e60e7257cc'),
                    UUID('17b1bed5-0981-4682-a9be-05e60e7257cc')],
                'TransactionId': [
                    0,
                    1,
                    2,
                    3],
                'SenderId': [
                    21,
                    21,
                    21,
                    21],
                'ReceiverId': [
                    24,
                    24,
                    24,
                    24],
                'ResourceId': [
                    10,
                    12,
                    14,
                    26],
                'Commodity': [
                    'fresh_uox',
                    'fresh_uox',
                    'fresh_uox',
                    'fresh_uox'],
                'Time': [
                    1,
                    1,
                    1,
                    2],
                'ObjId': [
                    9,
                    10,
                    11,
                    21],
                'Quantity': [
                    33000.0,
                    33000.0,
                    33000.0,
                    33000.0],
                'Units': [
                    'kg',
                    'kg',
                    'kg',
                    'kg'],
                'ReceiverPrototype': [
                    'Reactor_type1',
                    'Reactor_type1',
                    'Reactor_type1',
                    'Reactor_type1']})
        obs = tm.add_receiver_prototype(self.output_file1)
        assert_frame_equal(exp, obs[0:4])

    def test_get_annual_electricity(self):
        exp = pd.DataFrame(data={'Year': [1965], 'Energy': [0.120]})
        obs = tm.get_annual_electricity(self.output_file1)
        assert_frame_equal(exp, obs)

    def test_get_prototype_energy1(self):
        '''
        Tests function when the queried prototype is in the dataframe
        '''
        exp = pd.DataFrame(data={'Year': [1965, 1966], 'Energy': [0.02, 0.00]})
        obs = tm.get_prototype_energy(self.output_file1, 'Reactor_type2')
        assert_frame_equal(exp, obs[0:2])

    def test_get_prototype_energy2(self):
        '''
        Tests function when the queried prototype is not in the dataframe
        '''
        exp = pd.DataFrame(data={'Year': [1965, 1966], 'Energy': [0.00, 0.00]})
        obs = tm.get_prototype_energy(self.output_file1, 'Reactor_type3')
        assert_frame_equal(exp, obs[0:2])

    def test_get_lwr_energy1(self):
        '''
        Tests function when the queried non-LWR prototype is in the dataframe
        '''
        exp = pd.DataFrame(data={'Year': [1965, 1966], 'Energy': [0.10, 0.00]})
        obs = tm.get_lwr_energy(self.output_file1, ['Reactor_type2'])
        assert_frame_equal(exp, obs[0:2])

    def test_get_lwr_energy2(self):
        '''
        Tests function when the queried non-LWR prototype is not in the
        dataframe
        '''
        exp = pd.DataFrame(data={'Year': [1965, 1966], 'Energy': [0.12, 0.00]})
        obs = tm.get_lwr_energy(self.output_file1, ['Reactor_type3'])
        assert_frame_equal(exp, obs[0:2])
