import datetime as dt
import pandas as pd
from tools.misc.dates_misc import yesterday

def compare_close_intra(close_df, intra_df, quote_timing, date_range=[] ):

    # index reworking to dt
    intra_df.index = pd.to_datetime(intra_df.index)
    close_df.index = pd.to_datetime(close_df.index)

    # restricts intra_df's date range to user date range
    # -----------------------------------------------
    # restriction
    intra_df['date'] = intra_df.index.map(lambda x: x.date())
    intra_df = intra_df.loc[intra_df['date'].isin(date_range)]

    # restricts daily close to intra_df's date range
    # -----------------------------------------------
    intra_date_range = list(
        set([date.date() for date in intra_df.index.to_list()])
    )

    # we add a previous BD to our analysis exple: intra 26/08 needs 25/08
    intra_date_range.sort()
    try:
        intra_date_range.append(yesterday(intra_date_range[0]))
    except:
        print('')
    # restriction
    close_df.index = close_df.index.map(lambda x: x.date())
    close_df = close_df.loc[close_df.index.isin(intra_date_range)]

    # maps yesterday's closing price to intra_df, via dates in both df
    # -----------------------------------------------
    # adds date column and maps
    if quote_timing == 'close_yesterday':
        intra_df['date'] = intra_df.index.map(lambda x: yesterday(x.date()))
        intra_df['close_yesterday'] = intra_df['date'].map(close_df['Close'].to_dict())
        intra_df['return'] =\
            (intra_df['Close'] - intra_df['close_yesterday']) / intra_df['close_yesterday']

    elif quote_timing == 'open_today':
        intra_df['date'] = intra_df.index.map(lambda x: x.date())
        intra_df['open_today'] = intra_df['date'].map(close_df['Open'].to_dict())
        intra_df['return'] = \
            (intra_df['Close'] - intra_df['open_today']) / intra_df['open_today']

    # print('Intra vs last close_daily: returns computed')
    return intra_df

def compare_close_open_one_day(close_df, intra_df, date_close, date_open):
    # index reworking to dt
    intra_df.index = pd.to_datetime(intra_df.index)
    close_df.index = pd.to_datetime(close_df.index)

    close_df.index = close_df.index.map(lambda x: x.date())
    close = close_df.loc[close_df.index.isin([date_close])]['Close'][0]

    intra_df['date'] = intra_df.index.map(lambda x: x.date())
    open = intra_df.loc[intra_df['date'].isin([date_open])]['Close'][0]

    return abs(1-open/close)


def compare_close_open(close_df, intra_df, date_close, date_open):
    # index reworking to dt
    intra_df.index = pd.to_datetime(intra_df.index)
    close_df.index = pd.to_datetime(close_df.index)

    close_df.index = close_df.index.map(lambda x: x.date())
    close = close_df.loc[close_df.index.isin([date_close])]['Close'][0]

    intra_df['date'] = intra_df.index.map(lambda x: x.date())
    open = intra_df.loc[intra_df['date'].isin([date_open])]['Close'][0]

    return abs(1 - open / close)