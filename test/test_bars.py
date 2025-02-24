import pytest
import pandas as pd
import bars
import mlfinlab
from mlfinlab.data_structures.standard_data_structures import (get_dollar_bars,
                                                               get_tick_bars, get_volume_bars)


@pytest.fixture
def sample_data():
    data = pd.read_csv('data/ES_Trades.csv')
    yield data

# Test function using the fixture


def test_dollar_bars(sample_data):
    for df in sample_data:
        expected = get_dollar_bars(sample_data, threshold=70000000,
                                   batch_size=1000000, verbose=True)
        actual = bars.get_dollar_bars(sample_data, threhold=70000000)

        assert actual.shape == expected.shape


# Parameterized test for different inputs
# 'new_data' can be simply replaced with the file path where 'raw_tick_data' was saved if memory is an issue

# print('Creating Volume Bars')
# volume = get_volume_bars(new_data, threshold=28000,
#                          batch_size=1000000, verbose=False)
# 
# print('Creating Tick Bars')
# tick = get_tick_bars(new_data, threshold=5500,
#                      batch_size=1000000, verbose=False)


@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (2, 3, 5),
    (4, 5, 9),
])
def test_addition(a, b, expected):
    # Test that addition works as expected
    assert a + b == expected
