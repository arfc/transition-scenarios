import unittest
import numpy as np
import pandas as pd
import math
from pandas._testing import assert_frame_equal
from pandas._testing import assert_series_equal
import sys

sys.path.insert(0, '../')
import dakota_output as oup

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
        self.test_df1 = pd.DataFrame(
            data={
                'Time': [
                    0, 1, 1, 3], 'Quantity': [
                    2, 5, 6, 8], 'Commodity': [
                    'fresh_uox', 'spent_uox', 'fresh_uox', 'fresh_uox'],
                'Prototype': ['FuelCycle', 'LWR', 'Reactor_type1', 'LWR']})
        self.test_df2 = pd.DataFrame(
            data={
                'Time': [
                    0, 2, 3, 3, 5], 'Quantity': [
                    2, 5, 6, 8, 2], 'Commodity': [
                    'fresh_uox', 'spent_uox', 'fresh_uox', 'fresh_uox', 'spent_uox'],
                'Prototype': ['FuelCycle', 'LWR', 'Reactor_type1', 'LWR', 'Reactor_type1']})

    def test_merge_and_fillna_col1(self):
        '''
        Tests the function with the two default arguments supplied
        '''
        exp = pd.DataFrame(data = {'Time': [0, 3], 'Quantity':[2, 8], 
                            'Commodity':['fresh_uox', 'fresh_uox'], 
                            'Prototype':['FuelCyle','LWR']})
        obs = oup.merge_and_fillna_col(self.test_df1, self.test_df2, 'Time', 'Time')
        assert_frame_equal(exp, obs)

    def test_get_table_from_output1(self):
        '''
        Test function for the AgentEntry table from self.output_file1
        '''
        exp = pd.DataFrame(data={
            #'SimId': ["b'\x17\xb1\xbe\xd5\t\x81F\x82\xa9\xbe\x05\xe6\x0erW\xcc'",
            #"b'\x17\xb1\xbe\xd5\t\x81F\x82\xa9\xbe\x05\xe6\x0erW\xcc'",
            #"b'\x17\xb1\xbe\xd5\t\x81F\x82\xa9\xbe\x05\xe6\x0erW\xcc'",
            #"b'\x17\xb1\xbe\xd5\t\x81F\x82\xa9\xbe\x05\xe6\x0erW\xcc'"],
            'AgentId': [19,20,21,22],
            'Kind': ['Region', 'Inst','Facility','Facility'],
            'Spec': [':agents:NullRegion', ':agents:NullInst', ':cycamore:Source', ':cycamore:Sink'],
            'Prototype':['United States','FuelCycle','FuelSupply','Repository'],
            'ParentId':[-1, 19, 20, 20],
            'Lifetime':[-1, -1, -1, -1],
            'EnterTime':[0,0,0,0]
        })
        obs = oup.get_table_from_output(self.output_file1, 'AgentEntry')
        assert_frame_equal(exp, obs.drop('SimId', axis=1)[0:4])
    
    def test_get_table_from_output2(self):
        '''
        Test function for the Resource table from self.output_file1
        '''
        exp = pd.DataFrame(data={
            'ResourceId':[10,12,14,15],
            'ObjId':[9,10,11,9],
            'TimeCreated':[1, 1, 1,2],
            'Quantity':[33000.0, 33000.0, 33000.0, 33000.0],
            'Units':['kg','kg','kg','kg']
        })
        obs = oup.get_table_from_output(self.output_file1, 'Resources')
        assert_frame_equal(exp, obs.drop('SimId', axis=1)[0:4])

    def test_create_agents_table1(self):
        '''
        Test correct creation of the Agents DataFrame from output_file1, in 
        which agents are decommissioned.
        '''
        exp = pd.DataFrame(data={
            'AgentId':[19, 20, 21,22],
            'Kind':['Region', 'Inst', 'Facility', 'Facility'],
            'Spec':[':agents:NullRegion',':agents:NullInst', ':cycamore:Source', ':cycamore:Sink'],
            'Prototype':['United States','FuelCycle', 'FuelSupply','Repository'],
            'ParentId':[-1, 19, 20, 20],
            'Lifetime':[-1, -1, -1, -1],
            'EnterTime':[0, 0, 0, 0],
            'ExitTime':[-1.0, -1.0, -1.0, -1.0]
        })
        obs = oup.create_agents_table(self.output_file1)
        assert_frame_equal(exp,obs.drop('SimId', axis=1)[0:4])

    def test_create_agents_table2(self):
        '''
        Test correct creation of the Agents DataFrame from output_file2, in 
        which agents are not decommissioned.
        '''
        exp = pd.DataFrame(data={
            'AgentId':[19, 20, 21,22],
            'Kind':['Region', 'Inst', 'Facility', 'Facility'],
            'Spec':[':agents:NullRegion',':agents:NullInst', ':cycamore:Source', ':cycamore:Sink'],
            'Prototype':['United States','FuelCycle', 'FuelSupply','Repository'],
            'ParentId':[-1, 19, 20, 20],
            'Lifetime':[-1, -1, -1, -1],
            'EnterTime':[0, 0, 0, 0],
            'ExitTime':[-1.0, -1.0, -1.0, -1.0]
        })
        obs = oup.create_agents_table(self.output_file1)
        assert_frame_equal(exp,obs.drop('SimId', axis=1)[0:4])