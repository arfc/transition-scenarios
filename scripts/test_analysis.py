import unittest
import analysis as an
import numpy as np
import collections
import sqlite3 as lite


def get_sqlite():
    con = lite.connect('test.sqlite')
    con.row_factory = lite.Row
    with con:
        cur = con.cursor()
        return cur

class AnalysisTest(unittest.TestCase):
    """ Tests for analysis.py """

    def test_get_agent_ids(self):
        """ Test if get_agent_ids returns the right agentids"""
        cur = get_sqlite()
        ids = an.get_agent_ids(cur, 'reactor')
        answer = ['39', '40', '41', '42', '43', '44']
        self.assertCountEqual(ids, answer)

    def test_get_prototype_id(self):
        """ Test if get_prototype_id returns the right agentids"""
        cur = get_sqlite()
        ids = an.get_prototype_id(cur, 'lwr')
        answer = ['39', '40', '42']
        self.assertCountEqual(ids, answer)

    def test_get_timesteps(self):
        """ Tests if get_timesteps function outputs the right information"""
        cur = get_sqlite()
        init_year, init_month, duration, timestep = an.get_timesteps(cur)
        self.assertEqual(init_year, 2000)
        self.assertEqual(init_month, 1)
        self.assertEqual(duration, 10)
        self.assertEqual(timestep.all(), np.linspace(0, 9, num=10).all())

    def test_facility_commodity_flux(self):
        """ Tests if facility_commodity_flux works properly"""
        cur = get_sqlite()
        agent_ids = ['39', '40', '42']
        commod_list_send = ['uox_waste']
        commod_list_rec = ['uox']
        x = an.facility_commodity_flux(cur, agent_ids, commod_list_send, True)
        y = an.facility_commodity_flux(cur, agent_ids, commod_list_rec, False)
        answer_x = collections.OrderedDict()
        answer_y = collections.OrderedDict()
        answer_x['uox_waste'] = [0.0, 0.0, 0.3, 0.3, 0.7, 0.7, 1.0, 1.0, 1.0, 1.0]
        answer_y['uox'] = [0.0, 0.3, 0.6, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        self.assertEqual(x['uox_waste'], answer_x['uox_waste'])
        self.assertEqual(y['uox'], answer_y['uox'])

    def test_facility_commodity_flux_isotopics(self):
        """ Tests if facility_commodity_flux_isotopics works properly"""
        cur = get_sqlite()
        agent_ids = ['27']
        commod_list_send = ['reprocess_waste', 'uox_Pu']
        commod_list_rec = ['uox_waste']
        x = an.facility_commodity_flux_isotopics(cur, agent_ids, commod_list_send, True)
        y = an.facility_commodity_flux_isotopics(cur, agent_ids, commod_list_rec, False)
        answer_x = collections.OrderedDict()
        answer_y = collections.OrderedDict()
        answer_x['U235'] = [0, 0, 0, 2.64e-05, 2.64e-05, 6.28e-05,
                            6.28e-05, 8.92e-05, 8.92e-05, 8.92e-05]
        answer_y['U235'] = [0, 0, 0.01, 0.01, 0.03, 0.03,
                            0.04, 0.04, 0.04, 0.04]
        self.assertEqual(x['U235'], answer_x['U235'])
        self.assertEqual(y['U235'], answer_y['U235'])

    def test_get_stockpile(self):
        """ Tests if get_stockpile function works properly """
        cur = get_sqlite()
        facility = 'separations'
        pile_dict = an.get_stockpile(cur, facility)
        answer = collections.OrderedDict()
        answer[facility] = [ 0, 0, 0, 0.28, 0.28, 0.65, 0.65, 0.928, .0928, 0.928]
        self.assertEqual(pile_dict[facility], answer[facility])

    def test_get_swu_dict(self):
        """ Tests if get_swu_dict function works properly """
        cur = get_sqlite()
        swu_dict = an.get_swu_dict(cur)
        answer = collections.OrderedDict()
        answer['Enrichment1'] = [0, 1144, 2288, 3432, 3814, 3814, 3814, 3814, 3814, 3814]
        self.assertEqual(swu_dict('Enrichment1'), answer['Enrichment1'])

    def test_get_power_dict(self):
        """ Tests if get_power_dict function works properly """
        cur = get_sqlite()
        power_dict = an.get_power_dict(cur)
        lwr_inst = [0, 1, 1, 2, 1, 1, 0, 0, 0, 0]
        fr_inst = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(power_dict['lwr_inst'], lwr_inst)
        self.assertEqual(power_dict['fr_inst'], fr_inst)

    def u_util_calc(self):
        """ Tests if u_util_calc function works properly """
        cur = get_sqlite()
        x = an.u_util_calc(cur)
        answer = [0, 0.142, 0.142, 0.142, 0.142,
                  0.142, 0.142, 0.142, 0.142, 0.142]
        self.assertEqual(x, answer)

    def test_exec_string_receiverid(self):
        """Test if exec_string function prints the right thing
           When the query wants to find receiverid """
        string = an.exec_string([12, 35], 'receiverid', 'time, quantity')
        answer = ('SELECT time, quantity '
                  'FROM resources INNER JOIN transactions '
                  'ON transactions.resourceid = resources.resourceid '
                  'WHERE (receiverid = 12 OR receiverid = 35)')
        self.assertEqual(string, answer)

    def test_exec_string_commodity(self):
        """Test if exec_string function prints the right thing
           When the query wants to find commodity """
        string = an.exec_string(['uox', 'mox'], 'commodity', 'time, quantity')
        answer = ('SELECT time, quantity '
                  'FROM resources INNER JOIN transactions '
                  'ON transactions.resourceid = resources.resourceid '
                  'WHERE (commodity = "uox" OR commodity = "mox")')
        self.assertEqual(string, answer)

    def test_get_timeseries(self):
        """Test if get_timeseries returns the right timeseries list
           Given an in_list"""
        in_list = [[1, 245], [5, 375], [10, 411]]
        duration = 13
        x = an.get_timeseries(in_list, duration, False)
        print(x)
        answer = [0, 245, 0, 0, 0, 375, 0,
                  0, 0, 0, 411, 0, 0]
        self.assertEqual(x, answer)

    def test_kg_to_tons_no_cum(self):
        """Test if kg_to_tons boolean actually returns in tons
           for non-cumulative"""
        in_list = [[1, 245], [5, 375], [10, 411]]
        duration = 13
        x = an.get_timeseries(in_list, duration, True)
        answer = [0, 245, 0, 0, 0, 375, 0,
                  0, 0, 0, 411, 0, 0]
        answer = [x * 0.001 for x in answer]
        self.assertEqual(x, answer)

    
    def test_get_timeseries_cum(self):
        """Test if get_timeseries_cum returns the right timeseries list
           Given an in_list"""
        in_list = [[1, 245], [5, 375], [10, 411]]
        duration = 13
        x = an.get_timeseries_cum(in_list, duration, False)
        answer =[0, 245, 245, 245, 245, 245+375, 245+375,
                 245+375, 245+375, 245+375, 245+375+411,
                 245+375+411, 245+375+411]
        self.assertEqual(x, answer)

    def test_kg_to_tons_cum(self):
        """Test if kg_to_tons boolean actually returns in tons for cumulative"""
        in_list = [[1, 245], [5, 375], [10, 411]]
        duration = 13
        x = an.get_timeseries_cum(in_list, duration, True)
        answer =[0, 245, 245, 245, 245, 245+375, 245+375,
                 245+375, 245+375, 245+375, 245+375+411,
                 245+375+411, 245+375+411]
        answer = [y * 0.001 for y in answer]
        self.assertEqual(x, answer)

    def test_get_isotope_transactions(self):
        """Test if get_isotope_transactions function
           If it returns the right dictionary"""
        resources = [(1, 50, 2), (2, 70, 3), (4, 100, 4)]
        compositions = [(2, 922350000, .5), (2, 922380000, .5),
                        (3, 942390000, .3), (3, 942400000, .7),
                        (4, 942390000, .5), (4, 942410000, .5)]
        x = an.get_isotope_transactions(resources, compositions)
        answer = collections.defaultdict(list)
        answer[922350000].append((1, 25.0))
        answer[922380000].append((1, 25.0))
        answer[942390000].append((2, 21.0))
        answer[942390000].append((4, 50.0))
        answer[942400000].append((2, 49.0))
        answer[942410000].append((4, 50.0))
        for key in x:
            self.assertEqual(answer[key], x[key])


    def test_capacity_calc(self):
        """Test capacity_calc function"""
        governments = [('korea', 1), ('japan', 2)]
        timestep = np.linspace(0, 9, num=10)
        entry = [(600, 30, 1, 3), (1000, 31, 2, 4),
                 (700, 32, 1, 5), (500, 33, 2, 7)]
        exit_step = [(600, 30, 1, 7), (1000, 31, 2, 8),
                     (700, 32, 1, 9)]
        power_dict, num_dict = an.capacity_calc(governments,
                                                timestep, entry, exit_step)
        print(power_dict)
        print(num_dict)
        answer_power = collections.OrderedDict()
        answer_num = collections.OrderedDict()
        answer_power['korea'] = np.asarray([0, 0, 0, 600, 600, 1300, 1300,
                                           700, 700, 0])
        answer_power['japan'] = np.asarray([0, 0, 0, 0, 1000, 1000,
                                            1000, 1500, 500, 500])
        answer_power['korea'] = answer_power['korea'] * 0.001
        answer_power['japan'] = answer_power['japan'] * 0.001
        answer_num['korea'] = np.asarray([0, 0, 0, 1, 1, 2, 2,1, 1, 0])
        answer_num['japan'] = np.asarray([0, 0, 0, 0, 1, 1, 1, 2, 1, 1])
        for key in power_dict:
            self.assertTrue(np.array_equal(power_dict[key], answer_power[key]))
            self.assertTrue(np.array_equal(num_dict[key], answer_num[key]))


if __name__ == '__main__':
    unittest.main()