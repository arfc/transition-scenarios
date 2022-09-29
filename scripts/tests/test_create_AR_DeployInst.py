import create_AR_DeployInst as di
import unittest
import numpy as np
from pandas._testing import assert_frame_equal
from pandas._testing import assert_series_equal
import sys

sys.path.insert(0, '../')


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

    def test_determine_deployment_schedule1(self):
        '''
        Tests for a constant power demand of 400 MW for 40 time steps.
        '''
        exp = {
            'DeployInst': {
                'prototypes': {
                    'val': [
                        'Type1', 'Type2', 'Type2', 'Type2']}, 'build_times': {
                    'val': [
                        0, 0, 20, 25]}, 'n_build': {
                            'val': [
                                1, 1, 2, 1]}, 'lifetimes': {
                                    'val': [
                                        20, 25, 25, 25]}}}
        gap = np.repeat(400, 40)
        reactors = {'Type1': (300, 20), 'Type2': (150, 25)}
        obs = di.determine_deployment_schedule(gap, reactors)
        assert exp == obs

    def test_determine_deployment_schedule2(self):
        '''
        Tests with a defined prototype and build share (non-default values),
        defined as 50% for Type1 reactors.
        A constant power demand of 1000 MW for 40 time steps.
        '''
        exp = {
            'DeployInst': {
                'prototypes': {'val': [
                    'Type1', 'Type2', 'Type1', 'Type2', 'Type1', 'Type2']},
                'build_times': {
                    'val': [
                        0, 0, 20, 20, 25, 25]},
                'n_build': {'val': [
                    2, 3, 1, 2, 1, 1]},
                'lifetimes': {'val': [
                    20, 25, 20, 25, 20, 25]}}}
        gap = np.repeat(1000, 40)
        reactors = {'Type1': (300, 20), 'Type2': (150, 25)}
        obs = di.determine_deployment_schedule(gap, reactors, 'Type1', 50)
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
        Test creation of AR DeployInst for a demand of 1000 MWe starting in 2065,
        so the power from LWRs does not affect the advanced reactor deployment.
        A prototype with a defined buildshare is not specified.
        '''
        exp = {'DeployInst': {'prototypes': {'val': ['Xe-100', 'MMR', 'MMR']},
                              'lifetimes': {'val': [720, 240, 240]},
                              'n_build': {'val': [13, 3, 3]},
                              'build_times': {'val': [1200, 1200, 1440]}}}

        reactor_prototypes = {
            'Xe-100': (76, 720), 'MMR': (5, 240), 'VOYGR': (73, 720)}
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
        Test creation of AR DeployInst for a demand of 1000 MWe starting in 2065,
        so the power from LWRs does not affect the advanced reactor deployment.
        A prototype with a defined buildshare is specified: 50% MMR buildshare.
        '''
        exp = {
            'DeployInst': {
                'prototypes': {
                    'val': [
                        'VOYGR',
                        'Xe-100',
                        'MMR',
                        'VOYGR']},
                'lifetimes': {
                    'val': [
                        720,
                        720,
                        240,
                        720]},
                'n_build': {
                    'val': [
                        7,
                        6,
                        7,
                        1]},
                'build_times': {
                    'val': [
                        1200,
                        1200,
                        1200,
                        1440]}}}

        reactor_prototypes = {
            'Xe-100': (76, 720), 'MMR': (5, 240), 'VOYGR': (73, 720)}
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
            demand_eq,
            'VOYGR',
            50)
        assert exp['DeployInst']['prototypes']['val'] == obs['DeployInst']['prototypes']['val']
        assert exp['DeployInst']['lifetimes']['val'] == obs['DeployInst']['lifetimes']['val']
        assert exp['DeployInst']['n_build']['val'] == obs['DeployInst']['n_build']['val']
        assert exp['DeployInst']['build_times']['val'] == obs['DeployInst']['build_times']['val']
