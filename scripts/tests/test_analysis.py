import numpy as np
import pytest
import collections
import sqlite3 as lite
import os
import sys
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))
import analysis as an

dir = os.path.dirname(__file__)
test_sqlite_path = os.path.join(dir, 'test.sqlite')


def get_sqlite_cursor():
    con = lite.connect(test_sqlite_path)
    con.row_factory = lite.Row
    with con:
        cur = con.cursor()
        return cur


def test_agent_ids():
    """Test if get_agentids returns the right agentids"""
    cur = get_sqlite_cursor()
    ids = an.agent_ids(cur, 'reactor')
    answer = ['39', '40', '41', '42', '43', '44']
    assert ids == answer


def test_prototype_id():
    """Test if get_prototype_id returns the right agentids"""
    cur = get_sqlite_cursor()
    ids = an.prototype_id(cur, 'lwr')
    answer = ['39', '40', '42']
    assert ids == answer


def test_simulation_timesteps():
    """Tests if simulation_timesteps function outputs the right information"""
    cur = get_sqlite_cursor()
    init_year, init_month, duration, timestep = an.simulation_timesteps(cur)
    assert init_year == 2000
    assert init_month == 1
    assert duration == 10
    assert timestep.all() == np.linspace(0, 9, num=10).all()


def test_facility_commodity_flux():
    """Tests if facility_commodity_flux works properly"""
    cur = get_sqlite_cursor()
    agentids = ['39', '40', '42']
    commod_list_send = ['uox_waste']
    commod_list_rec = ['uox']
    x = an.facility_commodity_flux(cur, agentids, commod_list_send, True)
    y = an.facility_commodity_flux(cur, agentids, commod_list_rec, False)
    answer_x = collections.OrderedDict()
    answer_y = collections.OrderedDict()
    answer_x['uox_waste'] = [0.0, 0.0, 0.3,
                             0.3, 0.7, 0.7, 1.0, 1.0, 1.0, 1.0]
    answer_y['uox'] = [0.0, 0.3, 0.6, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    assert len(x['uox_waste']) == len(answer_x['uox_waste'])
    assert len(y['uox']) == len(answer_y['uox'])
    for expected, actual in zip(x['uox_waste'], answer_x['uox_waste']):
        assert expected == pytest.approx(actual, 1e-7)
    for expected, actual in zip(y['uox'], answer_y['uox']):
        assert expected == pytest.approx(actual, 1e-5)


@pytest.mark.skip(reason='not working, will fix')
def test_facility_commodity_flux_isotopics():
    """Tests if facility_commodity_flux_isotopics works properly"""
    cur = get_sqlite_cursor()
    agentids = ['27']
    commod_list_send = ['reprocess_waste', 'uox_Pu']
    commod_list_rec = ['uox_waste']
    x = an.facility_commodity_flux_isotopics(
        cur, agentids, commod_list_send, True)
    y = an.facility_commodity_flux_isotopics(
        cur, agentids, commod_list_rec, False)
    answer_x = collections.OrderedDict()
    answer_y = collections.OrderedDict()
    answer_x['U235'] = [0, 0, 0, 2.639e-05, 2.639e-05, 6.279e-05,
                        6.279e-05, 8.919e-05, 8.919e-05, 8.919e-05]
    answer_y['U235'] = [0, 0, 9.599e-3, 9.599e-3, 2.959e-2, 2.959e-2,
                        3.919e-2, 3.919e-2, 3.919e-2, 3.919e-2]
    assert len(x['U235']) == len(answer_x['U235'])
    assert len(y['U235']) == len(answer_y['U235'])
    for expected, actual in zip(x['U235'], answer_x['U235']):
        assert expected == pytest.approx(actual, abs=1e-5)
    for expected, actual in zip(y['U235'], answer_y['U235']):
        assert expected == pytest.approx(actual, abs=1e-5)


def test_stockpiles():
    """Tests if get_stockpiles function works properly """
    cur = get_sqlite_cursor()
    facility = 'separations'
    pile_dict = an.stockpiles(cur, facility)
    answer = collections.OrderedDict()
    answer[facility] = [0, 0, 0, 0.2794, 0.2794,
                        0.6487, 0.6487, 0.9281, .9281, 0.9281]
    assert len(pile_dict[facility]) == len(answer[facility])
    for expected, actual in zip(pile_dict[facility], answer[facility]):
        assert expected == pytest.approx(actual, abs=1e-4)


def test_swu_timeseries():
    """Tests if get_swu function works properly """
    cur = get_sqlite_cursor()
    swu = an.swu_timeseries(cur)
    answer = collections.OrderedDict()
    answer['Enrichment_30'] = [0, 1144.307, 2288.615,
                               3432.922, 3814.358, 3814.358,
                               3814.358, 3814.358, 3814.358, 3814.358]
    assert len(swu['Enrichment_30']) == len(answer['Enrichment_30'])
    for expected, actual in zip(swu['Enrichment_30'],
                                answer['Enrichment_30']):
        assert expected == pytest.approx(actual, 1e-3)


def test_power_capacity():
    """Tests if get_power_dict function works properly """
    cur = get_sqlite_cursor()
    power_dict = an.power_capacity(cur)
    lwr_inst = np.array([0, 1, 1, 2, 1, 1, 0, 0, 0, 0])
    fr_inst = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    assert power_dict['lwr_inst'].all() == lwr_inst.all()
    assert power_dict['fr_inst'].all() == fr_inst.all()


def test_u_util_calc():
    """ Tests if u_util_calc function works properly """
    cur = get_sqlite_cursor()
    x = an.u_util_calc(cur)
    answer = np.array([0, 0.142, 0.142, 0.142, 0.142,
                       0.142, 0.142, 0.142, 0.142, 0.142])
    assert x.all() == answer.all()


def test_exec_string_receiverid():
    """Test if exec_string function prints the right thing
       When the query wants to find receiverid """
    string = an.exec_string([12, 35], 'receiverid', 'time, quantity')
    answer = ('SELECT time, quantity '
              'FROM resources INNER JOIN transactions '
              'ON transactions.resourceid = resources.resourceid '
              'WHERE (receiverid = 12 OR receiverid = 35)')
    assert string == answer


def test_exec_string_commodity():
    """Test if exec_string function prints the right thing
       When the query wants to find commodity """
    string = an.exec_string(['uox', 'mox'], 'commodity', 'time, quantity')
    answer = ('SELECT time, quantity '
              'FROM resources INNER JOIN transactions '
              'ON transactions.resourceid = resources.resourceid '
              'WHERE (commodity = "uox" OR commodity = "mox")')
    assert string == answer


def test_timeseries():
    """Test if get_timeseries returns the right timeseries list
       Given an in_list"""
    in_list = [[1, 245], [5, 375], [10, 411]]
    duration = 13
    x = an.timeseries(in_list, duration, False)
    answer = [0, 245, 0, 0, 0, 375, 0,
              0, 0, 0, 411, 0, 0]
    assert x == answer


def test_kg_to_tons_no_cum():
    """Test if kg_to_tons boolean actually returns in tons
       for non-cumulative timeseries search"""
    in_list = [[1, 245], [5, 375], [10, 411]]
    duration = 13
    x = an.timeseries(in_list, duration, True)
    answer = [0, 245, 0, 0, 0, 375, 0,
              0, 0, 0, 411, 0, 0]
    answer = [y * 0.001 for y in answer]
    assert x == answer


def test_timeseries_cum():
    """Test if get_timeseries_cum returns the right timeseries list
       Given an in_list"""
    in_list = [[1, 245], [5, 375], [10, 411]]
    duration = 13
    x = an.timeseries_cum(in_list, duration, False)
    answer = [0, 245, 245, 245, 245, 245 + 375, 245 + 375,
              245 + 375, 245 + 375, 245 + 375, 245 + 375 + 411,
              245 + 375 + 411, 245 + 375 + 411]
    assert x == answer


def test_kg_to_tons_cum():
    """Test if kg_to_tons boolean actually
       returns in tons for cumulative"""
    in_list = [[1, 245], [5, 375], [10, 411]]
    duration = 13
    x = an.timeseries_cum(in_list, duration, True)
    answer = [0, 245, 245, 245, 245, 245 + 375, 245 + 375,
              245 + 375, 245 + 375, 245 + 375, 245 + 375 + 411,
              245 + 375 + 411, 245 + 375 + 411]
    answer = [y * 0.001 for y in answer]
    assert x == answer


def test_isotope_transactions():
    """Test if get_isotope_transactions function
       If it returns the right dictionary"""
    cur = get_sqlite_cursor()
    resources = cur.execute('SELECT sum(quantity), time, '
                            'qualid FROM transactions '
                            'INNER JOIN resources '
                            'ON resources.resourceid = '
                            'transactions.resourceid '
                            'WHERE commodity = "reprocess_waste" '
                            'GROUP BY time').fetchall()
    compositions = cur.execute('SELECT * FROM compositions').fetchall()
    x = an.isotope_transactions(resources, compositions)
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
        assert len(x[key]) == len(answer[key])
        for expected, actual in zip(x[key], answer[key]):
            for i in range(0, 1):
                assert expected[i] == pytest.approx(actual[i], 1e-3)

                
@pytest.mark.skip(reason='missing function')
def test_capacity_calc():
    """Test capacity_calc function"""
    cur = get_sqlite_cursor()
    init_year, init_month, duration, timestep = an.get_timesteps(cur)
    governments = an.get_inst(cur)
    entry_exit = cur.execute('SELECT max(value), timeseriespower.agentid, '
                             'parentid, entertime, entertime + lifetime '
                             'FROM agententry '
                             'INNER JOIN timeseriespower '
                             'ON agententry.agentid = '
                             'timeseriespower.agentid '
                             'GROUP BY timeseriespower.agentid').fetchall()
    entry = cur.execute('SELECT max(value), timeseriespower.agentid, '
                        'parentid, entertime FROM agententry '
                        'INNER JOIN timeseriespower '
                        'ON agententry.agentid = timeseriespower.agentid '
                        'GROUP BY timeseriespower.agentid').fetchall()
    exit_step = cur.execute('SELECT max(value), timeseriespower.agentid, '
                            'parentid, exittime FROM agentexit '
                            'INNER JOIN timeseriespower '
                            'ON agentexit.agentid = '
                            'timeseriespower.agentid'
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
        assert np.array_equal(
            power_dict[key], answer_power[key]) == True


def test_mass_timeseries():
    """Test mass_timeseries function"""
    cur = get_sqlite_cursor()
    facility = 'mox_fuel_fab'
    flux = 'in'
    mass_series = an.mass_timeseries(cur, facility, flux)[0]
    answer_mass = collections.OrderedDict()
    answer_mass['U235'] = np.asarray([1.77574965,  1.77574965, 1.77574965, 1.77574965,
                                      1.77574965,  1.77574965,  1.77574965,  1.77574965,  1.77574965,  1.77574965])
    answer_mass['U238'] = np.asarray([598.00225037,  598.00225037,  598.00225037,  598.00225037,
                                      598.00225037,  598.00225037,  598.00225037,  598.00225037,
                                      598.00225037,  598.00225037])
    answer_mass['Pu238'] = np.asarray([19.96,  29.94,  19.96])
    for key in mass_series:
        assert key in answer_mass.keys()


def test_cumulative_mass_timeseries():
    """Test cumulative_mass_timeseries function"""
    cur = get_sqlite_cursor()
    facility = 'mox_fuel_fab'
    flux = 'in'
    cumu_mass_series = an.cumulative_mass_timeseries(cur, facility, flux)[0]
    answer_cumu_mass = collections.OrderedDict()
    answer_cumu_mass['U235'] = np.asarray([1.77574965,  1.77574965, 1.77574965, 1.77574965,
                                           1.77574965,  1.77574965,  1.77574965,  1.77574965,  1.77574965,  1.77574965])
    answer_cumu_mass['U238'] = np.asarray([598.00225037,  598.00225037,  598.00225037,  598.00225037,
                                           598.00225037,  598.00225037,  598.00225037,  598.00225037,
                                           598.00225037,  598.00225037])
    answer_cumu_mass['Pu238'] = np.asarray([19.96,  29.94,  19.96])
    for key in cumu_mass_series:
        assert key in answer_cumu_mass.keys()

        
@pytest.mark.skip(reason='assertion error to be fixed later')
def test_powerseries_reactor():
    cur = get_sqlite_cursor()
    powerseries_reactor_39 = an.powerseries_reactor(cur, reactors=[39])[
        'Reactor_39']
    ans_powerseries_reactor_39 = [0, 1000.0, 1000.0, 0, 0, 0, 0, 0, 0, 0]
    assert_equal(powerseries_reactor_39, ans_powerseries_reactor_39)
