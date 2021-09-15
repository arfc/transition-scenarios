import numpy as np
import pandas as pd

import transition_metrics as tm


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
