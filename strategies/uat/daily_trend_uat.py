import pandas as pd
import datetime as dt
from databases.paths import QuotesPath, StrategiesPath
from tools.misc.database_misc import get_from_db, generate_folder
from tools.misc.dates_misc import yesterday
from tools.strategies_toolbox.intra_vs_close import compare_close_open_one_day, compare_close_intra

pd.options.mode.chained_assignment = None

"""
Trend following strat. Very basic: checks the openvsclose way and choose between long and short for the day.
Can be complemented with a moving-ave on udl.
"""
interval_comparison_dict = {'daily': 'daily', 'intraday': 'intra_2m'}
way_dict = {
    'bullish': 'UCO',
    'bearish': 'SCO'
}
gain_interval = 0.017
threshold = -0.015

def run_strat():

    udl_dict, fut_dict, date_r = load_data(
        underlyings=['^BCBCLI'],
        futures=['UCO', 'SCO'],
        period=47
    )
    close_df, intra_dfs = enrich_data(
        closeopen_df=udl_dict['^BCBCLI'],
        intra_dfs=fut_dict,
        date_filter=date_r
    )

    raw_res_list = []
    analyzed_res_list = []
    for date in date_r:
        intra_df = apply_logic(
            close_df,
            intra_dfs,
            date
        )
        if intra_df.empty:
            print('No data for ' + str(date.date()))
        else:
            raw_res = process_results(
                intra_df
            )

            analyzed_res = analyze_results(
                raw_res
            )
            raw_res_list.append(raw_res)
            analyzed_res_list.append(analyzed_res)
            print('Results computed for ' + str(date.date()))

    # aggregation of each date simu
    strat_raw_result = pd.concat(raw_res_list)
    strat_analyzed_result = pd.concat(analyzed_res_list)

    strat_raw_result.to_csv('strat_raw_result.csv')
    strat_analyzed_result.to_csv('strat_analyzed_result.csv')

def load_data(
        underlyings,
        futures,
        period
):
    """
    Loader
    """
    udl_data = {}
    fut_data = {}

    # date
    date_range = pd.bdate_range(
        end=dt.datetime.today(),
        periods=period,
        freq="C",
        holidays=["2023-09-04", "2023-06-19", "2023-07-04"]
    )

    for udl in underlyings:
        udl_data[udl] = get_from_db(
        path=QuotesPath + udl + f'\\daily_{udl}.csv',
        index_name='timestamp'
    )

    for fut in futures:
        fut_data[fut] = get_from_db(
            path=QuotesPath + fut + f'\\intra_2m_{fut}.csv',
            index_name='timestamp'
        )

    return udl_data, fut_data, date_range

def enrich_data(
        closeopen_df,
        intra_dfs,
        date_filter
    ):
    """
    Filters data with dates range.
    Computes openvsclose perf.
    Computes intraday returns.
    """
    # Filter
    closeopen_df, intra_dfs, filter_dates(
        closeopen_df,
        intra_dfs,
        date_filter
    )

    # Intra returns
    intra_dfs_filled = {}
    for udl, intra_df in intra_dfs.items():
        intra_df['date'] = intra_df.index.map(lambda x: x.date())
        intra_df['open_today'] = intra_df['date'].map(closeopen_df['Open'].to_dict())
        intra_df['return'] = \
            (intra_df['Close'] - intra_df['open_today']) / intra_df['open_today']
        intra_dfs_filled[udl] = intra_df

    # Close to open perf
    closeopen_df['return'] = \
        (closeopen_df['Close'] - closeopen_df['Open']) / closeopen_df['Open']

    return closeopen_df, intra_dfs_filled

def apply_logic(
        close_df,
        intra_dfs,
        date
):
    """
    We determine between bear and bull mkt
    We filter the proper df by date, so it's ready for the processing
    """
    daily_ret = close_df.loc[close_df.index == date.date()]['return'][0]

    if daily_ret > 0:
        intra_to_use = intra_dfs[way_dict['bullish']]
    elif daily_ret < 0:
        intra_to_use = intra_dfs[way_dict['bearish']]

    intra_to_use = intra_to_use.loc[intra_to_use['date'] == date.date()]

    return intra_to_use

def process_results(
        df
):
    """
    Buy @open, sell vs buy level with gain interval
    """
    # indicators
    position = 0
    buy_p = 0
    sell_p = 0
    colle = 0
    transaction_number = 0
    return_level_of_entry = 0

    # BS column rework
    df.reset_index(inplace=True)
    df['order_price'] = 0
    df['daily_return'] = 0
    df['position'] = 0
    df['colle'] = 0
    df['gain_interval'] = gain_interval
    df['transaction_number'] = 0
    col_dict = {col_name: num for num, col_name in zip(range(len(list(df.columns))), list(df.columns))}

    # go long
    df.iloc[1, col_dict['order_price']] = df.iloc[1, col_dict['Close']]
    df.iloc[1, col_dict['position']] = 1
    buy_p = df.iloc[1, col_dict['Close']]
    position += 1
    transaction_number += 1
    return_level_of_entry = df.iloc[1, col_dict['return']]

    # scroll through minutes, starting with second constatation
    for i in range(len(df))[2:]:

        # go short if return of entry + interval above gain interval
        # if df.iloc[i, col_dict['return']] >= return_level_of_entry + df.iloc[i, col_dict['gain_interval']] \
        #         and position == 1 \
        #         and colle == 0:
        #     df.iloc[i, col_dict['order_price']] = df.iloc[i, col_dict['Close']]
        #     df.iloc[i, col_dict['position']] = -1
        #     sell_p = df.iloc[i, col_dict['Close']]
        #     position -= 1

        # go short if return of entry + interval above gain interval
        if ((df.iloc[i, col_dict['Close']]/buy_p)-1)>= gain_interval \
                and position == 1 \
                and colle == 0:
            df.iloc[i, col_dict['order_price']] = df.iloc[i, col_dict['Close']]
            df.iloc[i, col_dict['position']] = -1
            sell_p = df.iloc[i, col_dict['Close']]
            position -= 1

        # go short if losses above threshold
        if position == 1 \
                and df.iloc[i, col_dict['timestamp']].hour <= 15 \
                and ((df.iloc[i, col_dict['Close']]/buy_p)-1)<= threshold \
                and colle == 0:
            df.iloc[i, col_dict['order_price']] = df.iloc[i, col_dict['Close']]
            df.iloc[i, col_dict['position']] = -1
            colle = 1
            sell_p = df.iloc[i, col_dict['Close']]
            position -= 1

        # go short at close
        if position == 1 \
                and df.iloc[i, col_dict['timestamp']].hour == 15 \
                and df.iloc[i, col_dict['timestamp']].minute >= 30 \
                and colle == 0:
            df.iloc[i, col_dict['order_price']] = df.iloc[i, col_dict['Close']]
            df.iloc[i, col_dict['position']] = -1
            colle = 1
            sell_p = df.iloc[i, col_dict['Close']]
            position -= 1

    if sell_p != 0:
        df['daily_return'] = (sell_p - buy_p) / buy_p
        df['colle'] = colle
        df['transaction_number'] = transaction_number

    return df

def analyze_results(res):

    macro_results = {}

    # Results gathering
    macro_results['daily_return'] = sum(res.set_index('date')['daily_return'].unique().tolist())
    # macro_results['daily_vol'] = res['daily_vol'].unique()[0]
    macro_results['gain_interval'] = res['gain_interval'].unique()[0]
    macro_results['colle'] = sum([res.set_index('date')['colle'].to_dict().values()][0])
    daily_transaction_number_list = [res.set_index('date')['transaction_number'].to_dict().values()][0]
    macro_results['total_transaction_number'] = sum(daily_transaction_number_list)
    macro_results['average_transaction_number'] =\
    sum(daily_transaction_number_list)/len(daily_transaction_number_list)

    macro_results_df = pd.DataFrame.from_dict(macro_results, orient='index').T

    return macro_results_df

def filter_dates(
        closeopen_df,
        intra_dfs,
        date_filter
):
    # index reworking to dt
    for intra_df in intra_dfs.values(): intra_df.index = pd.to_datetime(intra_df.index)
    closeopen_df.index = pd.to_datetime(closeopen_df.index, format='mixed')
    date_filter = [date.date() for date in date_filter]

    # restricts intra_df's date range to user date range
    # -----------------------------------------------
    # restriction
    intra_dfs_rwd = {}
    for udl, intra_df in intra_dfs.items():
        intra_df['date'] = intra_df.index.map(lambda x: x.date())
        intra_df = intra_df.loc[intra_df['date'].isin(date_filter)]
        intra_dfs_rwd[udl] = intra_df

    # restricts daily close to intra_df's date range
    # -----------------------------------------------
    intra_date_range = list(
        set([date.date() for date in list(intra_dfs.values())[0].index.to_list()])
    )

    # we add a previous BD to our analysis exple: intra 26/08 needs 25/08
    intra_date_range.sort()
    intra_date_range.append(yesterday(intra_date_range[0]))

    # restriction
    closeopen_df.index = closeopen_df.index.map(lambda x: x.date())
    close_df = closeopen_df.loc[closeopen_df.index.isin(intra_date_range)]

    return close_df, intra_dfs_rwd, intra_date_range

if __name__=='__main__':
    run_strat()