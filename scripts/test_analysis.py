import unittest
import analysis as an
import numpy as np
import collections
import sqlite3 as lite


dir = os.path.dirname(__file__)
test_sqlite_path = os.path.join(dir, 'test.sqlite')


def get_sqlite():
    con = lite.connect(test_sqlite_path)
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
        answer_x['uox_waste'] = [0.0, 0.0, 0.3,
                                 0.3, 0.7, 0.7, 1.0, 1.0, 1.0, 1.0]
        answer_y['uox'] = [0.0, 0.3, 0.6, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        self.assertEqual(len(x['uox_waste']), len(answer_x['uox_waste']))
        self.assertEqual(len(y['uox']), len(answer_y['uox']))
        for expected, actual in zip(x['uox_waste'], answer_x['uox_waste']):
            self.assertAlmostEqual(expected, actual, delta=1e-7)
        for expected, actual in zip(y['uox'], answer_y['uox']):
            self.assertAlmostEqual(expected, actual, delta=1e-5)

    def test_facility_commodity_flux_isotopics(self):
        """ Tests if facility_commodity_flux_isotopics works properly"""
        cur = get_sqlite()
        agent_ids = ['27']
        commod_list_send = ['reprocess_waste', 'uox_Pu']
        commod_list_rec = ['uox_waste']
        x = an.facility_commodity_flux_isotopics(
            cur, agent_ids, commod_list_send, True)
        y = an.facility_commodity_flux_isotopics(
            cur, agent_ids, commod_list_rec, False)
        answer_x = collections.OrderedDict()
        answer_y = collections.OrderedDict()
        answer_x['U235'] = [0, 0, 0, 2.639e-05, 2.639e-05, 6.279e-05,
                            6.279e-05, 8.919e-05, 8.919e-05, 8.919e-05]
        answer_y['U235'] = [0, 0, 9.599e-3, 9.599e-3, 2.959e-2, 2.959e-2,
                            3.919e-2, 3.919e-2, 3.919e-2, 3.919e-2]
        self.assertEqual(len(x['U235']), len(answer_x['U235']))
        self.assertEqual(len(y['U235']), len(answer_y['U235']))
        for expected, actual in zip(x['U235'], answer_x['U235']):
            self.assertAlmostEqual(expected, actual, delta=1e-7)
        for expected, actual in zip(y['U235'], answer_y['U235']):
            self.assertAlmostEqual(expected, actual, delta=1e-5)

    def test_get_stockpile(self):
        """ Tests if get_stockpile function works properly """
        cur = get_sqlite()
        facility = 'separations'
        pile_dict = an.get_stockpile(cur, facility)
        answer = collections.OrderedDict()
        answer[facility] = [0, 0, 0, 0.2794, 0.2794,
                            0.6487, 0.6487, 0.9281, .9281, 0.9281]
        self.assertEqual(len(pile_dict[facility]), len(answer[facility]))
        for expected, actual in zip(pile_dict[facility], answer[facility]):
            self.assertAlmostEqual(expected, actual, delta=1e-4)

    def test_get_swu_dict(self):
        """ Tests if get_swu_dict function works properly """
        cur = get_sqlite()
        swu_dict = an.get_swu_dict(cur)
        answer = collections.OrderedDict()
        answer['Enrichment_30'] = [0, 1144.307, 2288.615,
                                   3432.922, 3814.358, 3814.358,
                                   3814.358, 3814.358, 3814.358, 3814.358]
        self.assertEqual(len(swu_dict['Enrichment_30']),
                         len(answer['Enrichment_30']))
        for expected, actual in zip(swu_dict['Enrichment_30'], answer['Enrichment_30']):
            self.assertAlmostEqual(expected, actual, delta=1e-3)

    def test_get_power_dict(self):
        """ Tests if get_power_dict function works properly """
        cur = get_sqlite()
        power_dict = an.get_power_dict(cur)
        lwr_inst = np.array([0, 1, 1, 2, 1, 1, 0, 0, 0, 0])
        fr_inst = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(power_dict['lwr_inst'].all(), lwr_inst.all())
        self.assertEqual(power_dict['fr_inst'].all(), fr_inst.all())

    def test_u_util_calc(self):
        """ Tests if u_util_calc function works properly """
        cur = get_sqlite()
        x = an.u_util_calc(cur)
        answer = np.array([0, 0.142, 0.142, 0.142, 0.142,
                           0.142, 0.142, 0.142, 0.142, 0.142])
        self.assertEqual(x.all(), answer.all())

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
        answer = [0, 245, 245, 245, 245, 245 + 375, 245 + 375,
                  245 + 375, 245 + 375, 245 + 375, 245 + 375 + 411,
                  245 + 375 + 411, 245 + 375 + 411]
        self.assertEqual(x, answer)

    def test_kg_to_tons_cum(self):
        """Test if kg_to_tons boolean actually returns in tons for cumulative"""
        in_list = [[1, 245], [5, 375], [10, 411]]
        duration = 13
        x = an.get_timeseries_cum(in_list, duration, True)
        answer = [0, 245, 245, 245, 245, 245 + 375, 245 + 375,
                  245 + 375, 245 + 375, 245 + 375, 245 + 375 + 411,
                  245 + 375 + 411, 245 + 375 + 411]
        answer = [y * 0.001 for y in answer]
        self.assertEqual(x, answer)

    def test_get_isotope_transactions(self):
        """Test if get_isotope_transactions function
           If it returns the right dictionary"""
        cur = get_sqlite()
        resources = cur.execute('SELECT sum(quantity), time, qualid FROM transactions '
                                'INNER JOIN resources '
                                'ON resources.resourceid = transactions.resourceid '
                                'WHERE commodity = "reprocess_waste" '
                                'GROUP BY time').fetchall()
        compositions = cur.execute('SELECT * FROM compositions').fetchall()
        x = an.get_isotope_transactions(resources, compositions)
        answer = collections.defaultdict(list)
        answer[922350000].append((3, 0.02639))
        answer[922350000].append((5, 0.03639))
        answer[922350000].append((7, 0.02639))
        answer[922380000].append((3, 0.5336))
        answer[922380000].append((5, 0.7036))
        answer[922380000].append((7, 0.53360))
        answer[942380000].append((3, 0.04))
        answer[942380000].append((5, 0.06))
        answer[942380000].append((7, 0.04))
        for key in x:
            self.assertEqual(len(x[key]), len(answer[key]))
            for expected, actual in zip(x[key], answer[key]):
                for i in range(0, 1):
                    self.assertAlmostEqual(expected[i], actual[i], delta=1e-3)

    def test_capacity_calc(self):
        """Test capacity_calc function"""
        cur = get_sqlite()
        init_year, init_month, duration, timestep = an.get_timesteps(cur)
        governments = an.get_inst(cur)
        entry_exit = cur.execute('SELECT max(value), timeseriespower.agentid, '
                                 'parentid, entertime, entertime + lifetime '
                                 'FROM agententry '
                                 'INNER JOIN timeseriespower '
                                 'ON agententry.agentid = timeseriespower.agentid '
                                 'GROUP BY timeseriespower.agentid').fetchall()
        entry = cur.execute('SELECT max(value), timeseriespower.agentid, '
                            'parentid, entertime FROM agententry '
                            'INNER JOIN timeseriespower '
                            'ON agententry.agentid = timeseriespower.agentid '
                            'GROUP BY timeseriespower.agentid').fetchall()
        exit_step = cur.execute('SELECT max(value), timeseriespower.agentid, '
                                'parentid, exittime FROM agentexit '
                                'INNER JOIN timeseriespower '
                                'ON agentexit.agentid = timeseriespower.agentid'
                                ' INNER JOIN agententry '
                                'ON agentexit.agentid = agententry.agentid '
                                'GROUP BY timeseriespower.agentid').fetchall()
        power_dict = an.capacity_calc(governments, timestep, entry_exit)
        answer_power = collections.OrderedDict()
        answer_power['lwr_inst'] = np.asarray([0, 1, 2, 2, 2, 1, 1, 0, 0, 0])
        answer_power['fr_inst'] = np.asarray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        answer_power['sink_source_facilities'] = np.asarray(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        for key in power_dict:
            self.assertTrue(np.array_equal(
                power_dict[key], answer_power[key]))


if __name__ == '__main__':
    unittest.main()
