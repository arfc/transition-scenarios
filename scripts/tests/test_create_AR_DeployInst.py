import unittest
import numpy as np
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
        self.test_file = 'output_metrics_testfile.xml'
        self.deploy_inst_dict = {
            'DeployInst': {
                'prototypes': {
                    'val': [
                        'Sink_HLW',
                        'ANO-1',
                        'ANO-2',
                        'BEAVER_VALLEY-1']},
                'build_times': {
                    'val': [
                        '900',
                        '117',
                        '169',
                        '138']},
                'n_build': {
                    'val': [
                        '1',
                        '1',
                        '1',
                        '1']}}}
        self.AR_DI_dict = {
            'DeployInst': {
                'prototypes': {
                    'val': [
                        'Type2',
                        'Type1',
                        'Type3']},
                'build_times': {
                    'val': [
                        '0',
                        '10',
                        '30']},
                'n_build': {
                    'val': [
                        '1',
                        '1',
                        '1']},
                'lifetimes': {
                    'val': [
                        '720',
                        '240',
                        '360'
                    ]
                }}}
        self.deployed_reactor_dict = {
            'lifetime': [
                717,
                715,
                715],
            'prototypes': [
                'ANO-1',
                'ANO-2',
                'BEAVER_VALLEY-1'],
            'n_build': [
                1,
                1,
                1],
            'build_times': [
                117,
                169,
                138]}
        self.power_dict = {'ANO-1': 836, 'ANO-2': 988, 'BEAVER_VALLEY-1': 908}
        self.simulation_dict = {'simulation':
                                {'control':
                                    {'decay': 'lazy', 'duration': '1000',
                                     'startmonth': '1', 'startyear': '2000'}}}
        self.reactor_prototypes = {
            'Type1': (
                80, 3), 'Type2': (
                25, 5), 'Type3': (
                50, 10)}
        self.deploy_schedule = {'DeployInst': {
            'prototypes': {
                                'val': ['Type1']},
            'n_build': {
                'val': [2]},
            'build_times': {
                'val': [0]},
            'lifetimes': {
                'val': [3]}
        }}

    def test_convert_xml_to_dict(self):
        '''
        Test with test_outfile
        '''
        exp = {'DeployInst':
               {'prototypes':
                {'val': ['Sink_HLW', 'ANO-1', 'ANO-2', 'BEAVER_VALLEY-1']},
                'build_times':
                    {'val': ['900', '117', '169', '138']},
                'n_build':
                    {'val': ['1', '1', '1', '1']}}
               }
        obs = di.convert_xml_to_dict(self.test_file)
        assert exp == obs

    def test_get_deployinst_dict(self):
        '''
        Test with test_dict
        '''
        exp = {'lifetime': [717, 715, 715],
               'prototypes': ['ANO-1', 'ANO-2', 'BEAVER_VALLEY-1'],
               'n_build': [1, 1, 1],
               'build_times': [117, 169, 138]}
        obs = di.get_deployinst_dict(
            self.deploy_inst_dict,
            self.power_dict,
            "../../input/haleu/inputs/united_states/reactors/")
        assert exp == obs

    def test_get_powers(self):
        '''
        Test based on the ANO-1.xml file in the haleu project directory.
        Should probably add in a conditional for if any xml file found isn't
        for a cycamore reactor
        '''
        obs = di.get_powers("../../input/haleu/inputs/united_states/reactors/")
        assert obs['ANO-1'] == '774.6376'

    def test_get_lifetime(self):
        '''
        Test for lifetime of ANO-1 prototype
        '''
        exp = 717
        obs = di.get_lifetime('./', 'ANO-1')
        assert exp == obs

    def test_get_deployed_power(self):
        '''
        Test the power deployed as specific points in time,
        time = 0, 120, 140, 200, 840, 860, 900
        to test time points between reactor commissionings and
        decommissionings
        '''
        exp1 = np.linspace(0, 999, 1000)
        obs1, obs2 = di.get_deployed_power(
            self.power_dict, self.deployed_reactor_dict, 1000)
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
        demand = np.repeat(2500, 1000)
        power = np.linspace(0, 3000, 1000)
        obs = di.determine_power_gap(power, demand)
        assert 2500 == obs[0]
        assert 0 == obs[999]

    def test_determine_deployment_order1(self):
        '''
        Test when the values in the dictionary are different
        '''
        reactors = {'Type1': (100, 40), 'Type2': (500, 40)}
        exp = ['Type2', 'Type1']
        obs = di.determine_deployment_order(reactors)
        assert exp == obs

    def test_determine_deployment_order2(self):
        '''
        Test when the values in the dictionary are the same, will
        put keys in the order they are defined in the dictionary
        '''
        reactors = {'Beta': (500, 40), 'Alpha': (500, 40)}
        exp = ['Beta', 'Alpha']
        obs = di.determine_deployment_order(reactors)
        assert exp == obs

    def test_update_di(self):
        '''
        Add the deployment of 2 Type2 reactors at timestep 40 with a
        lifetime of 720 timesteps
        '''
        exp = {
            'DeployInst': {
                'prototypes': {
                    'val': [
                        'Type2',
                        'Type1',
                        'Type3',
                        'Type2']},
                'build_times': {
                    'val': [
                        '0',
                        '10',
                        '30',
                        40]},
                'n_build': {
                    'val': [
                        '1',
                        '1',
                        '1',
                        2]},
                'lifetimes': {
                    'val': [
                        '720',
                        '240',
                        '360',
                        720]}}}
        obs = di.update_di(self.AR_DI_dict, 'Type2', 2, 40, 720)
        assert exp == obs

    def test_update_power_demand(self):
        '''
        Test for the deployment of 2 Type2s, with power out 25 and lifetime
        of 5, each against a demand of 100 for 10 timesteps
        '''
        power_gap_exp = np.repeat(100, 10)
        power_gap_exp[0:6] = 50
        value_exp = 50
        power_gap_obs, value_obs = di.update_power_demand(
            np.repeat(100, 10), 0, 100, 2, self.reactor_prototypes, 'Type2')
        assert power_gap_exp.all() == power_gap_obs.all()
        assert value_exp == value_obs

    def test_deploy_with_share1(self):
        '''
        Test for when a single prototype share is specified
        '''
        exp = 4
        obs = di.deploy_with_share(
            self.reactor_prototypes, {
                'Type2': 50}, 200, 'Type2')
        assert exp == obs

    def test_deploy_with_share2(self):
        '''
        Test for when multiple prototype shares are specified
        '''
        exp = 4
        obs = di.deploy_with_share(
            self.reactor_prototypes, {
                'Type2': 50, 'Type3': 5}, 200, 'Type2')
        assert exp == obs

    def test_deploy_with_share3(self):
        '''
        Test when the calculated value is negative
        '''
        exp = 0
        obs = di.deploy_with_share(self.reactor_prototypes,
                                   {'Type2': 50},
                                   -100,
                                   'Type2')
        assert exp == obs

    def test_deploy_without_share1(self):
        '''
        Test when the first prototype in the list is specified
        '''
        exp = 2
        obs = di.deploy_without_share('Type1', ['Type1', 'Type3', 'Type2'],
                                      self.reactor_prototypes, 220)
        assert exp == obs

    def test_deploy_without_share2(self):
        '''
        Test when the last prototype in the list is specified
        '''
        exp = 9
        obs = di.deploy_without_share('Type2', ['Type1', 'Type3', 'Type2'],
                                      self.reactor_prototypes, 220)
        assert exp == obs

    def test_deploy_without_share3(self):
        '''
        Test when the calculated number is negative'''
        exp = 0
        obs = di.deploy_without_share('Type1',
                                      ['Type1', 'Type3', 'Type2'],
                                      self.reactor_prototypes,
                                      -100)
        assert exp == obs

    def test_redeploy_reactors1(self):
        '''
        Test when the calculated number is greater than the previous deployment
        '''
        exp = 2
        deploy_schedule = {'DeployInst': {
            'prototypes': {
                'val': ['Type1']},
            'n_build': {
                'val': [2]},
            'build_times': {
                'val': [0]},
            'lifetimes': {
                'val': [3]}
        }}
        obs = di.redeploy_reactors(250,
                                   'Type1',
                                   self.reactor_prototypes,
                                   deploy_schedule,
                                   0)
        assert exp == obs

    def test_redeploy_reactors2(self):
        '''
        Test when the calculated number is less than the previous deployment
        '''
        exp = 1
        deploy_schedule = {'DeployInst': {
            'prototypes': {
                'val': ['Type1']},
            'n_build': {
                'val': [2]},
            'build_times': {
                'val': [0]},
            'lifetimes': {
                'val': [3]}
        }}
        obs = di.redeploy_reactors(80,
                                   'Type1',
                                   self.reactor_prototypes,
                                   deploy_schedule,
                                   0)
        assert exp == obs

    def test_redeploy_reactors3(self):
        '''
        Test when the calculated number is equal to the previous deployment
        '''
        exp = 2

        obs = di.redeploy_reactors(150,
                                   'Type1',
                                   self.reactor_prototypes,
                                   self.deploy_schedule,
                                   0)
        assert exp == obs

    def test_redeploy_reactors4(self):
        '''
        Test when the calculated number is negative
        '''
        exp = 0
        obs = di.redeploy_reactors(-150,
                                   'Type1',
                                   self.reactor_prototypes,
                                   self.deploy_schedule,
                                   0)
        assert exp == obs

    def test_determine_deployment_schedule1(self):
        '''
        Tests for a constant power demand of 440 MW for 10 time steps and
        no build share specified
        '''
        exp = {
            'DeployInst': {
                'prototypes': {
                    'val': [
                        'Type1', 'Type2', 'Type1', 'Type2', 'Type1', 'Type1']},
                'build_times': {
                    'val': [
                        0, 0, 3, 5, 6, 9]},
                'n_build': {
                    'val': [
                        5, 2, 5, 2, 5, 5]},
                'lifetimes': {
                    'val': [
                        3, 5, 3, 5, 3, 3]}}}
        gap = np.repeat(440, 10)
        obs = di.determine_deployment_schedule(gap, self.reactor_prototypes)
        assert exp == obs

    def test_determine_deployment_schedule2(self):
        '''
        Tests with a defined prototype and build share (non-default values),
        defined as 50% for Type2 reactors.
        A constant power demand of 595 MW for 10 time steps, which tests
        for a different number of the Type 2 reactors under redeployed.
        '''
        exp = {
            'DeployInst': {
                'prototypes': {
                    'val': [
                        'Type1',
                        'Type3',
                        'Type2',
                        'Type1',
                        'Type2',
                        'Type1',
                        'Type1']},
                'build_times': {
                    'val': [
                        0, 0, 0, 3, 5, 6, 9]},
                'n_build': {'val': [
                    3, 2, 12, 3, 11, 3, 3]},
                'lifetimes': {'val': [
                    3, 10, 5, 3, 5, 3, 3]}}}
        gap = np.repeat(595, 10)
        obs = di.determine_deployment_schedule(gap, self.reactor_prototypes,
                                               {'Type2': 50})
        assert exp == obs

    def test_determine_deployment_schedule3(self):
        '''
        Tests for a constant power demand of 575 MW for 11 time steps and
        no build share specified. The longer time period of this test
        tests when multiple types of advanced reactors are decommissioned
        at the same time, testing that the same number of each prototype
        get redeployed.
        '''
        exp = {
            'DeployInst': {
                'prototypes': {
                    'val': [
                        'Type1',
                        'Type3',
                        'Type2',
                        'Type1',
                        'Type2',
                        'Type1',
                        'Type1',
                        'Type3',
                        'Type2'
                    ]},
                'build_times': {
                    'val': [
                        0, 0, 0, 3, 5, 6, 9, 10, 10]},
                'n_build': {'val': [
                    6, 1, 2, 6, 2, 6, 6, 1, 2]},
                'lifetimes': {'val': [
                    3, 10, 5, 3, 5, 3, 3, 10, 5]}}}
        gap = np.repeat(556, 11)
        obs = di.determine_deployment_schedule(gap, self.reactor_prototypes)
        assert exp == obs

    def test_determine_deployment_schedule4(self):
        '''
        Tests for a variable power demand for 12 timesteps that
        decreases with time, and no build share specified. This tests
        for a decreasing number of prototypes as the demand decreases.
        This tests the redeployment numbers when only one prototype
        needs to be redeployed and when multiple are redeployed
        '''
        exp = {
            'DeployInst': {
                'prototypes': {
                    'val': ['Type1',
                            'Type3',
                            'Type2',
                            'Type1',
                            'Type2',
                            'Type1',
                            'Type1',
                            'Type3',
                            'Type2',
                            ]},
                'build_times': {
                    'val': [
                        0, 0, 0, 3, 5, 6, 9, 10, 10]},
                'n_build': {'val': [
                    6, 1, 2, 6, 1, 6, 3, 1, 1]},
                'lifetimes': {'val': [
                    3, 10, 5, 3, 5, 3, 3, 10, 5]}}}
        gap = np.array([556, 556, 556, 556, 540, 540, 540, 540, 300, 300, 300])
        obs = di.determine_deployment_schedule(gap, self.reactor_prototypes)
        assert exp == obs

    def test_determine_deployment_schedule5(self):
        '''
        Tests for a variable power demand for 11 timesteps that
        increases with time, and no build share specified. This tests
        for a decreasing number of prototypes as the demand decreases.
        This tests the redeployment numbers when only one prototype
        needs to be redeployed and when multiple are redeployed
        '''
        exp = {
            'DeployInst': {
                'prototypes': {
                    'val': ['Type1',
                            'Type3',
                            'Type2',
                            'Type1',
                            'Type2',
                            'Type2',
                            'Type1',
                            'Type1',
                            'Type3',
                            'Type2',
                            'Type1',
                            'Type2',
                            'Type3',
                            'Type2'
                            ]},
                'build_times': {
                    'val': [
                        0, 0, 0, 3, 4, 5, 6, 8, 8, 8, 9, 9, 10, 10]},
                'n_build': {'val': [
                    6, 1, 2, 6, 1, 2, 6, 3, 1, 1, 6, 1, 1, 2]},
                'lifetimes': {'val': [
                    3, 10, 5, 3, 5, 5, 3, 3, 10, 5, 3, 5, 10, 5]}}}
        gap = np.array([556, 556, 556, 556, 600, 600, 600, 600, 900, 900, 900])
        obs = di.determine_deployment_schedule(gap, self.reactor_prototypes)
        assert exp == obs

    def test_determine_deployment_schedule6(self):
        '''
        Tests for a variable power demand for 12 timesteps that
        decreases with time, and a build share specified. This tests
        for a decreasing number of prototypes as the demand decreases.
        This tests the redeployment numbers when only one prototype
        needs to be redeployed and when multiple are redeployed
        '''
        exp = {
            'DeployInst': {
                'prototypes': {
                    'val': ['Type1',
                            'Type3',
                            'Type2',
                            'Type1',
                            'Type2',
                            'Type1',
                            'Type3',
                            'Type2',
                            ]},
                'build_times': {
                    'val': [
                        0, 0, 0, 3, 5, 6, 10, 10]},
                'n_build': {'val': [
                    3, 1, 12, 3, 10, 3, 1, 10]},
                'lifetimes': {'val': [
                    3, 10, 5, 3, 5, 3, 10, 5]}}}
        gap = np.array([556, 556, 556, 556, 540, 540, 540, 540, 300, 300, 300])
        obs = di.determine_deployment_schedule(gap,
                                               self.reactor_prototypes,
                                               {'Type2': 50})
        assert exp == obs

    def test_write_lwr_deployinst(self):
        '''
        Test combination of functions to create a DeployInst of LWRs when
        10% get license extensions. The lifetime values tested are for the
        SinkHLW facility, the LWR with the largest capacity (Grand Gulf-1),
        the last LWR on the list to receive an extension (Susquehanna-1),
        and the ext LWR on the list (Seabrook-1) to ensure it does not get
        extended.
        '''
        obs = di.write_lwr_deployinst(
            10.0,
            "../../input/haleu/inputs/united_states/" +
            "buildtimes/UNITED_STATES_OF_AMERICA/" +
            "deployinst.xml",
            "../../database/lwr_power_order.txt")
        assert obs['DeployInst']['lifetimes']['val'][0] == 600
        assert obs['DeployInst']['lifetimes']['val'][39] == 960
        assert obs['DeployInst']['lifetimes']['val'][100] == 960
        assert obs['DeployInst']['lifetimes']['val'][89] == 720

    def test_write_AR_deployinst1(self):
        '''
        Test creation of AR DeployInst for a demand of 1000 MWe starting in
        2065, so the power from LWRs does not affect the advanced reactor
        deployment. A prototype with a defined buildshare is not specified.
        '''
        exp = {
            'DeployInst': {
                'prototypes': {
                    'val': [
                        'Type1', 'Type2', 'Type2']}, 'lifetimes': {
                    'val': [
                        720, 240, 240]}, 'n_build': {
                            'val': [
                                13, 3, 3]}, 'build_times': {
                                    'val': [
                                        1200, 1200, 1440]}}}

        reactor_prototypes = {
            'Type1': (76, 720), 'Type2': (5, 240), 'Type3': (73, 720)}
        demand_eq = np.zeros(1500)
        demand_eq[1200:] = 1000
        lwr_DI = di.convert_xml_to_dict(
            "../../input/haleu/inputs/united_states/buildtimes/" +
            "UNITED_STATES_OF_AMERICA/deployinst.xml")
        obs = di.write_AR_deployinst(
            lwr_DI,
            "../../input/haleu/inputs/united_states/reactors/",
            1500,
            reactor_prototypes,
            demand_eq)
        assert exp['DeployInst']['prototypes']['val'] == obs['DeployInst']['prototypes']['val']
        assert exp['DeployInst']['n_build']['val'] == obs['DeployInst']['n_build']['val']
        assert exp['DeployInst']['build_times']['val'] == obs['DeployInst']['build_times']['val']
        assert exp['DeployInst']['lifetimes']['val'] == obs['DeployInst']['lifetimes']['val']

    def test_write_AR_deployinst2(self):
        '''
        Test creation of AR DeployInst for a demand of 1000 MWe starting in
        2065, so the power from LWRs does not affect the advanced reactor
        deployment. A prototype with a defined build share is specified: 50%
        Type2 build share.
        '''
        exp = {
            'DeployInst': {
                'prototypes': {
                    'val': [
                        'Type1',
                        'Type3',
                        'Type2',
                        'Type1',
                        'Type2',
                        'Type1',
                        'Type1']},
                'build_times': {
                    'val': [
                        1200, 1200, 1200, 1203, 1205, 1206, 1209]},
                'n_build': {'val': [
                    2, 2, 9, 2, 8, 2, 2]},
                'lifetimes': {'val': [
                    3, 10, 5, 3, 5, 3, 3]}}}

        demand_eq = np.zeros(1210)
        demand_eq[1200:] = 440
        lwr_DI = di.convert_xml_to_dict(
            "../../input/haleu/inputs/united_states/buildtimes/" +
            "UNITED_STATES_OF_AMERICA/deployinst.xml")
        obs = di.write_AR_deployinst(
            lwr_DI,
            "../../input/haleu/inputs/united_states/reactors/",
            1210,
            self.reactor_prototypes,
            demand_eq,
            {'Type2': 50})
        assert exp['DeployInst']['prototypes']['val'] == obs['DeployInst']['prototypes']['val']
        assert exp['DeployInst']['lifetimes']['val'] == obs['DeployInst']['lifetimes']['val']
        assert exp['DeployInst']['n_build']['val'] == obs['DeployInst']['n_build']['val']
        assert exp['DeployInst']['build_times']['val'] == obs['DeployInst']['build_times']['val']
