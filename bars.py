import numpy as np
import pandas as pd
import statsmodels
from typing import Generator, Iterable, Optional, Tuple, Union, List


def crop_data_frame_in_batches(df: pd.DataFrame, chunksize: int) -> List[pd.DataFrame]:
    for _, chunk in df.groupby(np.arange(len(df)) // chunksize):
        yield chunk


def batch_iterator(batch_size: int, file_path_or_df: Union[str, Iterable[str], pd.DataFrame]) -> Generator[pd.DataFrame, None, None]:

    if isinstance(file_path_or_df, (list, tuple)):
        for file_path in file_path_or_df:
            for batch in pd.read_csv(file_path, chunksize=batch_size, parse_dates=[0]):
                yield batch
    elif isinstance(file_path_or_df, str):
        for batch in pd.read_csv(file_path_or_df, chunksize=batch_size, parse_dates=[0]):
            yield batch
    elif isinstance(file_path_or_df, pd.DataFrame):
        for batch in crop_data_frame_in_batches(file_path_or_df, batch_size):
            yield batch
    else:
        raise ValueError("value err")


def get_time_bars(df: pd.DataFrame, resolution: str = "S", num_units: int = 1, mapping={'price': 'Price', 'volume': 'Volume', 'time': 'datetime', 'symbol': 'Symbol'}):
    result = []
    tick_num = 0
    prev_price = None
    tick_diff = 0
    prev_tick_rule = None
    open_price = None

    stats = {
        "ticks": 0,
        "dollar_value": 0,
        "volume": 0,
        "buy_volume": 0
    }
    high_price, low_price = - np.inf, np.inf

    threshold = int(1e9) * num_units * {
        'D': 60 * 60 * 24,
        'H': 60 * 60,
        'MIN': 60,
        'S': 1
    }[resolution]

    curr_symbol = None
    window_end = None

    cols = [
        "date_time",
        "tick_num",
        "instrument",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "buy_volume",
        "num_ticks",
        "dollar_value",
    ]

    for index, row in df.iterrows():

        date_time = row[mapping['time']]

        # round tick boundary up
        timestamp_threshold = (
            (date_time.as_unit('ns').value + (threshold - 1)) // threshold) * threshold

        if window_end is None:
            window_end = timestamp_threshold

        if window_end < timestamp_threshold:
            # The next observation doesn't fall into our current time window - so generate a new bar.
            result.append(
                [
                    window_end,  # time
                    tick_num,
                    curr_symbol,  # symbol
                    open_price,  # open
                    high_price,  # high
                    low_price,   # low
                    prev_price,  # close
                    stats['volume'],
                    stats['buy_volume'],
                    stats['ticks'],
                    stats['dollar_value']
                ]
            )
            open_price = None
            high_price, low_price = -np.inf, np.inf
            stats = {
                "ticks": 0,
                "dollar_value": 0,
                "volume": 0,
                "buy_volume": 0
            }
            window_end = timestamp_threshold

        price = np.float64(row[mapping['price']])
        volume = row[mapping['volume']]
        tick_num += 1
        dollar_value = price * volume
        symbol = row[mapping['symbol']]
        curr_symbol = symbol

        tick_diff = price - prev_price if prev_price is not None else 0
        signed_tick = np.sign(tick_diff) if tick_diff != 0 else prev_tick_rule
        prev_tick_rule = signed_tick
        prev_price = price

        if open_price is None:
            open_price = price

        high_price, low_price = max(high_price, price), min(low_price, price)
        stats['ticks'] += 1
        stats['dollar_value'] += dollar_value
        stats['volume'] += volume

        if signed_tick == 1:
            stats['buy_volume'] += volume

    return pd.DataFrame(result, columns=cols)


def standard_bars(df, key, threshold, mapping={'price': 'Price', 'volume': 'Volume', 'time': 'datetime', 'symbol': 'Symbol'}):
    result = []

    tick_num = 0
    prev_price = None
    tick_diff = 0
    prev_tick_rule = None
    open_price = None

    stats = {
        "ticks": 0,
        "dollar_value": 0,
        "volume": 0,
        "buy_volume": 0
    }
    high_price, low_price = - np.inf, np.inf

    curr_symbol = None
    window_end = None

    cols = [
        "date_time",
        "tick_num",
        "instrument",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "buy_volume",
        "num_ticks",
        "dollar_value",
    ]

    for index, row in df.iterrows():
        date_time = row[mapping['time']]
        price = np.float64(row[mapping['price']])
        volume = row[mapping['volume']]
        tick_num += 1
        dollar_value = price * volume
        symbol = row[mapping['symbol']]
        curr_symbol = symbol

        tick_diff = price - prev_price if prev_price is not None else 0
        signed_tick = np.sign(tick_diff) if tick_diff != 0 else prev_tick_rule
        prev_tick_rule = signed_tick
        prev_price = price

        if open_price is None:
            open_price = price

        high_price, low_price = max(high_price, price), min(low_price, price)
        stats['ticks'] += 1
        stats['dollar_value'] += dollar_value
        stats['volume'] += volume

        if signed_tick == 1:
            stats['buy_volume'] += volume

        if stats[key] > threshold:
            result.append([
                date_time,  # time
                tick_num,
                curr_symbol,  # symbol
                open_price,  # open
                high_price,  # high
                low_price,   # low
                prev_price,  # close
                stats['volume'],
                stats['buy_volume'],
                stats['ticks'],
                stats['dollar_value']
            ])
            open_price = None
            high_price, low_price = -np.inf, np.inf
            stats = {
                "ticks": 0,
                "dollar_value": 0,
                "volume": 0,
                "buy_volume": 0
            }

    return pd.DataFrame(result, columns=cols)


def get_volume_bars(df, threshold):
    return standard_bars(df, 'volume', threshold)


def get_tick_bars(df, threshold):
    return standard_bars(df, 'ticks', threshold)


def get_dollar_bars(df, threshold):
    return standard_bars(df, 'dollar_value', threshold)


def get_rolled_series(df, match_end=True, mapping={'price_open': 'Price', 'price_close': 'Price', 'symbol': 'Symbol'}):
    # series.set_index('date_time', inplace=True)
    roll_dates = df[mapping['symbol']].drop_duplicates(keep='first').index
    gaps = df[mapping['price_close']] * 0
    iloc = list(df.index)
    iloc = [iloc.index(i) - 1 for i in roll_dates]

    gaps.loc[roll_dates[1:]] = df[mapping['price_open']].loc[roll_dates[1:]
                                                             ] - df[mapping['price_close']].iloc[iloc[1:]].values
    gaps = gaps.cumsum()
    if match_end:
        gaps -= gaps.iloc[-1]  # roll backward
    return gaps


def get_rolled_returns(df, match_end=True, open_col='open', close_col='close', symbol_col='symbol'):
    roll_dates = df[symbol_col].drop_duplicates(keep='first').index
    gaps = df[close_col] * 0
    iloc = list(df.index)
    iloc = [iloc.index(i) - 1 for i in roll_dates]

    gaps.loc[roll_dates[1:]] = df[open_col].loc[roll_dates[1:]
                                                ] - df[close_col].iloc[iloc[1:]].values
    gaps = gaps.cumsum()

    if match_end:
        gaps -= gaps.iloc[-1]  # roll backward

    rolled_df = df.copy(deep=True)
    for fld in [open_col, close_col]:
        rolled_df[fld] -= gaps
    rolled_df['returns'] = rolled_df[close_col].diff() / df[close_col].shift(1)
    rolled_df['rprice'] = (1 + rolled_df['returns']).cumprod()
    return rolled_df


if __name__ == "__main__":

    trades = pd.read_csv('data/ES_Trades.csv')
    trades = trades.iloc[:100000]

    trades['datetime'] = pd.to_datetime(trades['Date'] + ' ' + trades['Time'])

    # time_bars = get_time_bars(trades)
    # print(time_bars.head())

    dollar_bars = get_dollar_bars(trades, threshold=7 * 1e7)
    print(dollar_bars.head())

    volume_bars = get_volume_bars(trades, threshold=28000)
    print(volume_bars.head())

    tick_bars = get_tick_bars(trades, threshold=5500)
    print(tick_bars.head())

    ticks_rolled = get_rolled_returns(
        tick_bars, match_end=True, symbol_col='instrument')
    print(ticks_rolled.head())


