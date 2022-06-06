import unittest
import numpy as np
import pandas as pd
import math
from pandas._testing import assert_frame_equal
from pandas._testing import assert_series_equal
import sys

sys.path.insert(0, '../')
import create_AR_DeployInst as di

class Test_static_info(unittest.TestCase):
    def setUp(self):
        '''
        This defines the output files and a test dictionary to use within the
        test suite.

        The first output file (output_metrics_testfile1.xml) is a simple 
        xml input file for Cyclus

        The second output file (output_metric_testfile2.xml) is an xml 
        input for just a cycamore:DeployInst. This is a separate file 
        because the functions interpret this to be a separate dictionary 
        from the main simulation file. 

        A third file is needed: ANO-1.xml, which should be placed in this 
        directory. This is a separate file because the functions tested
        here assume the modular file structure created by using 
        `creat_cyclus_input.py`/.
        '''
        self.test_file1 = 'output_metrics_testfile1.xml'
        self.test_file2 = 'output_metrics_testfile2.xml'
        self.deploy_inst_dict = {'DeployInst':
                {'prototypes':
                    {'val':['Sink_HLW', 'ANO-1','ANO-2', 'BEAVER_VALLEY-1']},
                'build_times':
                    {'val':['900', '117', '169','138']},
                'n_build':
                    {'val':['1','1','1','1']}}
                }
        self.deployed_reactor_dict = {'lifetime': [717, 715, 715],
                'prototypes':['ANO-1', 'ANO-2', 'BEAVER_VALLEY-1'],
                'n_build':[1,1,1],
                'build_times':[117,169,138]}
        self.power_dict = {'ANO-1':836, 'ANO-2':988, 'BEAVER_VALLEY-1':908}
        self.simulation_dict = {'simulation':
                                {'control':
                                    {'decay':'lazy', 'duration':'1000',
                                    'startmonth':'1', 'startyear':'2000'}}}

    def test_convert_xml_to_dict(self):
        '''
        Test with test_outfile1
        '''
        exp = {'DeployInst':
                {'prototypes':
                    {'val':['Sink_HLW', 'ANO-1','ANO-2', 'BEAVER_VALLEY-1']},
                'build_times':
                    {'val':['900', '117', '169','138']},
                'n_build':
                    {'val':['1','1','1','1']}}
                }
        obs = di.convert_xml_to_dict(self.test_file2)
        assert exp == obs

    def test_get_deployinst_dict(self):
        '''
        Test with test_dict
        '''
        exp = {'lifetime': [717, 715, 715],
                'prototypes':['ANO-1', 'ANO-2', 'BEAVER_VALLEY-1'],
                'n_build':[1,1,1],
                'build_times':[117,169,138]}
        obs = di.get_deployinst_dict(self.deploy_inst_dict, self.power_dict, 
        "../../input/haleu/inputs/united_states/reactors/")
        assert exp == obs

    def test_get_simulation_duration(self):
        '''
        Test with sim_dict
        '''
        exp = 1000
        obs = di.get_simulation_duration(self.simulation_dict)
        assert exp == obs

    def test_get_pris_powers(self):
        '''
        Test for specific reactors in the 
        '''
        exp = {'ANO-1':836, 'ANO-2':988, 'BEAVER_VALLEY-1':908}
        obs = di.get_pris_powers('UNITED STATES OF AMERICA', '../../database/',2020)
        assert exp['ANO-1'] == obs['ANO-1']
        assert exp['BEAVER_VALLEY-1'] == obs['BEAVER_VALLEY-1']

    def test_get_lifetimes(self):
        '''
        Test for lifetime of ANO-1 prototype
        '''
        exp = 717
        obs = di.get_lifetime('ANO-1', './')
        assert exp == obs

    def test_insert_lifetimes(self):
        '''
        Test with self.deployed_dict, using path to files in 
        input/haleu/inputs/reactors.
        '''
        exp = {'lifetime': [717, 715, 715],
                'prototypes':['ANO-1', 'ANO-2', 'BEAVER_VALLEY-1'],
                'n_build':[1,1,1],
                'build_times':[117,169,138]}
        obs = di.insert_lifetimes('../../input/haleu/inputs/united_states/reactors/', self.deployed_reactor_dict)
        assert exp == obs

    def test_get_deployed_power(self):
        '''
        Test the power deployed as specific points in time, 
        time = 0, 120, 140, 200, 840, 860, 900
        to test time points between reactor commissionings and 
        decommissionings
        '''
        exp1 = np.linspace(0,999,1000)
        obs1, obs2 = di.get_deployed_power(self.power_dict, self.deployed_reactor_dict, 1000)
        assert 0 == obs2[0]
        assert 836 == obs2[120]
        assert 1744 == obs2[140]
        assert 2732 == obs2[200]
        assert 1896 == obs2[840]
        assert 988 == obs2[860]
        assert 0 == obs2[900]
        assert np.all(exp1 == obs1)

    def test_determine_power_gap(self):
        '''
        Test agains a power demand of 2500 across the whole simulation
        against a linearly increasing power supply from 0 to 3000, to 
        test supply values greater than and equal to demand. 
        '''
        demand = np.repeat(2500,1000)
        power = np.linspace(0,3000,1000)
        obs = di.determine_power_gap(power, demand)
        assert 2500 == obs[0]
        assert 0 == obs[999]

    def test_determine_deployment_order1(self):
        '''
        Test when the values in the dictionary are different
        '''
        reactors = {'Type1':(100,40), 'Type2':(500, 40)}
        exp = ['Type2', 'Type1']
        obs = di.determine_deployment_order(reactors)
        assert exp == obs

    def test_determine_deployment_order2(self):
        '''
        Test when the values in the dictionary are the same, will 
        put keys in the order they are defined in the dictionary
        '''
        reactors = { 'Beta':(500, 40), 'Alpha':(500, 40)}
        exp = ['Beta', 'Alpha']
        obs = di.determine_deployment_order(reactors)
        assert exp == obs

    def test_determine_deployment_schedule(self):
        '''
        '''
        exp = {'DeployInst': {'prototypes': {'val': ['Type1', 'Type2', 'Type2', 'Type2']},
                            'build_times': {'val': [1,1, 20, 25]},
                            'n_build': {'val': [1, 1, 2, 1]},
                            'lifetimes': {'val': [20, 25, 25, 25]}}}
        gap = np.repeat(400,40)
        reactors = {'Type1': (300, 20), 'Type2':(150, 25)}
        obs = di.determine_deployment_schedule(gap, reactors)
