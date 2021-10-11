import numpy as np
import pandas as pd
from uuid import UUID
from pandas._testing import assert_series_equal
from pandas._testing import assert_frame_equal

import transition_metrics as tm

class file_df_info(object):
    def __init__(self):
        self.output_file1 = 'transition_metrics_decommission_test.sqlite'
        self.output_file2 = 'transition_metrics_nodecommission_test.sqlite'
        self.test_df = pd.DataFrame(data={'Time': [0,1,1,3], 
        'Quantity':[2,5,6,8], 'Commodity':['fresh_uox', 'spent_uox', 
        'fresh_uox', 'fresh_uox']})

def test_get_metrics():     
    obs = 'Test_case' #tm.get_metrics(self.output_file)
    assert isinstance(obs, str)

def test_rx_commission_decommission1():
    exp = pd.Series(data={0:0.0, 1:0.0, 
        2:1.0, 3:2.0, 4:2.0, 5:2.0, 6:2.0}, name='lwr_total')
    non_lwr = ['United States', 'FuelCycle', 'FuelSupply', 
        'Repository', 'UNITED_STATES_OF_AMERICA', 
        'Reactor_type1_enter', 'Reactor_type1_exit']
    file_info = file_df_info()
    df = tm.rx_commission_decommission(file_info.output_file1, non_lwr)
    obs = df['lwr_total']
    assert_series_equal(exp,obs)

def test_rx_commission_decommission2():
    exp = pd.Series(data={0:0.0, 1:0.0, 
        2:1.0, 3:2.0, 4:2.0, 5:2.0, 6:2.0}, name='lwr_total')
    non_lwr = ['United States', 'FuelCycle', 'FuelSupply', 
        'Repository', 'UNITED_STATES_OF_AMERICA', 
        'Reactor_type1']
    file_info = file_df_info()
    df = tm.rx_commission_decommission(file_info.output_file2, non_lwr)
    obs = df['lwr_total']
    assert_series_equal(exp,obs)

def test_add_year():
    exp = pd.Series(data={0:1965.08, 1: 1965.33, 2: 1965.58, 3:1965.83,
    4:1966.08}, name='Year')
    data = np.array([(1,2,3),(4,5,6), (7,8,9), (10,11,12), (13, 14, 15)])
    df = pd.DataFrame(data, columns=['Time', 'Data1', 'Data2'])
    obs = tm.add_year(df)
    assert_series_equal(exp, obs['Year'])

def test_get_transactions():
    exp = pd.DataFrame(data = {'Time': [0,1,1], 'SimId':[0, 
        UUID('6af6d305-e3be-4790-8920-b3f3bec3d6f7'), UUID('6af6d305-e3be-4790-8920-b3f3bec3d6f7')],
        'TransactionId':[0.0, 0.0, 1.0], 'ResourceId':[0.0, 10.0, 12.0],
        'ObjId':[0.0, 9.0, 10.0], 'SenderId':[0.0, 21.0, 21.0], 
        'ReceiverId':[0.0, 24.0, 24.0], 'Commodity':[0, 'fresh_uox', 'fresh_uox'],
        'Units':[0, 'kg', 'kg'], 'Quantity':[0.0, 33000.0, 33000.0]})
    file_info = file_df_info()
    obs = tm.get_transactions(file_info.output_file1)
    assert_frame_equal(exp, obs[0:3])
        
def test_sum_and_add_missing_time():
    exp = pd.DataFrame(data={'Time':[0,1,2,3], 'Quantity':[2.0,11.0, 0.0, 8.0]})
    test_df = file_df_info()
    obs = tm.sum_and_add_missing_time(test_df.test_df)
    assert_frame_equal(exp, obs[0:4])

def test_find_commodity_transactions1():
    exp = pd.DataFrame(data={'Time':[0,1,3], 'Quantity':[2, 6, 8], 
        'Commodity':['fresh_uox', 'fresh_uox', 'fresh_uox']}).set_index([pd.Index([0,2,3])])
    df_info = file_df_info()
    obs = tm.find_commodity_transcations(df_info.test_df, 'fresh_uox')
    assert_frame_equal(exp, obs)

def test_find_commodity_transactions2():
    exp = pd.DataFrame(data={'Time':[], 'Quantity':[], 
        'Commodity':[]})
    df_info = file_df_info()
    obs = tm.find_commodity_transcations(df_info.test_df, 'tails')
    assert_frame_equal(exp, obs, check_dtype=False)

def test_calculate_feed1():
    exp = 10
    product = 5
    tails = 5
    obs = tm.calculate_feed(product, tails)
    assert exp == obs


def test_calculate_feed2():
    exp = np.repeat(10, 3)
    product = np.repeat(5, 3)
    tails = np.repeat(5, 3)
    obs = tm.calculate_feed(product, tails)
    assert np.all(exp == obs)


def test_calculate_feed3():
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
    obs = tm.calculate_feed(product['a'], tails['a'])
    assert np.all(exp == obs)
