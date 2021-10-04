import numpy as np
import pandas as pd

import transition_metrics as tm

class test_reading_output(object):
    def __init__(self):
        self.output_file = 'test_transition_metrics.sqlite'

    def test_get_metrics(self):
        exp = Evaluator 
        obs = tm.get_metrics(self.output_file)
        assert isinstance(obs, exp)

    #def test_rx_commission_decommission1():

        assert_frame_equal(exp,obs)
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
