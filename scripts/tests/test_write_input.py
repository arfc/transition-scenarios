import numpy as np
import collections
import os
import sys
path = os.path.realpath(__file__)
sys.path.append(os.path.dirname(os.path.dirname(path)))
import write_input as wi

dir = os.path.dirname(__file__)
test_database_path = os.path.join(dir, 'test_database.csv')

def test_read_csv():
    """Test if read_csv returns the correct list with key"""
    reactor_array = wi.read_csv(test_database_path)
    print(type(reactor_array))
    test_dict = {}
    test_dict['country1'] = reactor_array[0]['country'].decode('utf-8')
    test_dict['country3'] = reactor_array[2]['country'].decode('utf-8')
    # makes sure the test reactor is filtered out
    test_dict['capacity1'] = reactor_array[0]['net_elec_capacity']
    test_dict['capacity3'] = reactor_array[2]['net_elec_capacity']

    answer_dict = {}
    answer_dict['country1'] = 'France'
    answer_dict['country3'] = 'Czech_Republic'
    answer_dict['capacity1'] = 1495
    answer_dict['capacity3'] = 1200
    assert test_dict == answer_dict

def test_filter_test_reactors():
    """Test if filter__reactors filters reactors with
       net electricity capacity less than 100Mwe"""
    test = np.array([('foo', 85), ('bar', 1200)],
                    dtype=[('name', 'S10'), ('net_elec_capacity', 'i4')])
    answer = np.array([('bar', 1200)],
                      dtype=[('name', 'S10'), ('net_elec_capacity', 'i4')])
    assert wi.filter_test_reactors(test) == answer

def test_get_ymd_ceil():
    """Test if get_ymd gets the correct year, month, and day"""
    ceil = wi.get_ymd(20180225)
    answer = (2018, 3)
    assert ceil == answer

def test_get_ymd_floor():
    """Test if get_ymd gets the correct year, month, and day"""
    floor = wi.get_ymd(20180301)
    answer = (2018, 3)
    assert floor == answer

def test_get_lifetime():
    """Test if get_lifetime calculates the right lifetime"""
    start_date = 19700101
    end_date = 20070225
    lifetime = 446
    assert wi.get_lifetime(start_date, end_date) == lifetime

def test_get_lifetime_no_endtime():
    """Test if get_lifetime calculates the right lifetime
       given no endtime"""
    assert wi.get_lifetime(19700101, -1) == 720

def test_get_entrytime():
    """Test if get_entrytime calculates the correct entrytime"""
    init_date = 19700101
    start_date = 20070225
    assert wi.get_entrytime(init_date, start_date) == 446

def test_refine_name():
    """Test if name is refined correctly"""
    string = 'Charles(Bukowski)'
    string = string.encode('utf-8')
    assert wi.refine_name(string) == 'Charles'

