import pandas as pd
import datetime as dt
from tools.misc.database_misc import get_from_db
from tools.misc.dates_misc import yesterday
from databases.paths import QuotesPath, StudyResultsPath
pd.options.mode.chained_assignment = None

"""
This script objective is to determine if there is any empirical evidence of correlation between
%return of open_today/close_yesterday and the max return of the day. Both in abs value.
For instance if BCBCLI moved 1% at open today vs close yesterday is it more likely to hit 2% max during the day

The end-goal is to adapt our gain_interval
"""

def run_study():

    udl_dict, fut_dict, date_r = load_data(
        underlyings=['^BCBCLI','UCO', 'SCO'],
        futures=['UCO', 'SCO'],
        period=170
    )
    close_df, intra_dfs, shifted_date_r = enrich_data(
        closeopen_df=udl_dict,
        intra_dfs=fut_dict,
        date_filter=date_r
    )

    for udl, df in close_df.items():
        mapping_max = intra_dfs['SCO'].set_index('date')['max_return_of_the_day'].to_dict()
        mapping_min = intra_dfs['SCO'].set_index('date')['min_return_of_the_day'].to_dict()
        mapping_high = intra_dfs['SCO'].set_index('date')['highest_return_in_absolute_terms_return_of_the_day'].to_dict()
        mapping_abs = intra_dfs['SCO'].set_index('date')['max_abs_return_of_the_day'].to_dict()
        df['date'] = df.index
        df['max_return_of_the_day'] = df['date'].map(mapping_max)
        df['min_return_of_the_day'] = df['date'].map(mapping_min)
        df['highest_return_in_absolute_terms_return_of_the_day'] = df['date'].map(mapping_high)
        df['max_abs_return_of_the_day'] = df['date'].map(mapping_abs)
        df.to_csv(StudyResultsPath + f'daily_raw_data_{udl}.csv')
    for udl, df in intra_dfs.items():
        df.to_csv(StudyResultsPath + f'intra_raw_data_{udl}.csv')
    print('')
    # raw_res_list = []
    # analyzed_res_list = []
    # for date in shifted_date_r:
    #     intra_df = apply_logic(
    #         close_df,
    #         intra_dfs,
    #         date
    #     )
    #     if intra_df.empty:
    #         print('No data for ' + str(date.date()))
    #     else:
    #         raw_res = process_results(
    #             intra_df
    #         )
    #
    #         analyzed_res = analyze_results(
    #             raw_res
    #         )
    #         raw_res_list.append(raw_res)
    #         analyzed_res_list.append(analyzed_res)
    #         print('Results computed for ' + str(date.date()))
    #
    # # aggregation of each date simu
    # strat_raw_result = pd.concat(raw_res_list)
    # strat_analyzed_result = pd.concat(analyzed_res_list)
    #
    # strat_raw_result.to_csv(BacktestResultsPath + 'daily_trend_raw_result.csv')
    # strat_analyzed_result.to_csv(BacktestResultsPath + 'daily_trend_analyzed_result.csv')

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
        holidays=["2023-09-04",
                  "2023-06-19",
                  "2023-07-04",
                  "2023-05-29",
                  "2023-01-16",
                  "2023-02-20",
                  "2023-04-07"]
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
    closeopen_df, intra_dfs = filter_dates(
        closeopen_df,
        intra_dfs,
        date_filter
    )

    # Daily returns
    closeopen_df_rwd = {}
    for udl, daily_df in closeopen_df.items():
        
        # We shift the close and thus can't calculate perf for one date (cause we don't have T-1 close)
        daily_df = daily_df.sort_index(ascending=True)
        daily_df = daily_df.assign(CloseShifted=lambda x: x['Close'].shift(1))
        # date_filter = date_filter.drop([daily_df.loc[daily_df['CloseShifted'].isna()].index[0]])
        daily_df = daily_df.loc[daily_df['CloseShifted'].notna()]
        # Close to open perf using open of BCBCLI @8
        daily_df['return'] = \
            (daily_df['Open'] - daily_df['CloseShifted']) / daily_df['CloseShifted']
        daily_df['abs_return'] = \
            abs((daily_df['Open'] - daily_df['CloseShifted']) / daily_df['CloseShifted'])
        closeopen_df_rwd[udl] = daily_df
        
    # Intra returns
    intra_dfs_filled = {}
    for udl, intra_df in intra_dfs.items():
        intra_df['max_abs_return_of_the_day'] = None
        intra_df['date'] = intra_df.index.map(lambda x: x.date())
        intra_df['close_yesterday'] = intra_df['date'].map(closeopen_df_rwd[udl]['CloseShifted'].to_dict())
        intra_df['return'] = \
            (intra_df['Close'] - intra_df['close_yesterday']) / intra_df['close_yesterday']
        for date in date_filter:
            # We take the maximum of the abs values of returns, per day
            # We could have taken the trading range, max - min. but this study is to apply on a single direction start
            max_per_day = intra_df.loc[intra_df['date'] == date.date(), 'return'].max()
            min_per_day = intra_df.loc[intra_df['date'] == date.date(), 'return'].min()
            intra_df.loc[intra_df['date'] == date.date(), 'max_return_of_the_day'] = max_per_day
            intra_df.loc[intra_df['date'] == date.date(), 'min_return_of_the_day'] = min_per_day
            if abs(max_per_day)>abs(min_per_day):
                intra_df.loc[
                    intra_df['date'] == date.date(), 'highest_return_in_absolute_terms_return_of_the_day'] = max_per_day

            else:
                intra_df.loc[
                    intra_df['date'] == date.date(), 'highest_return_in_absolute_terms_return_of_the_day'] = min_per_day

            # Absolute terms
            max_abs_per_day = intra_df.loc[intra_df['date'] == date.date(), 'return'].apply(lambda x : abs(x)).max()
            intra_df.loc[intra_df['date'] == date.date(), 'max_abs_return_of_the_day'] = max_abs_per_day

        intra_dfs_filled[udl] = intra_df

    # # Close to open perf using open of BCBCLI @8
    # closeopen_df['return'] = \
    #     (closeopen_df['Open'] - closeopen_df['CloseShifted']) / closeopen_df['CloseShifted']

    # # Close to open perf using open of BCBCLI @9:30
    # closeopen_df['return'] = \
    #     (closeopen_df['CloseShifted'] - closeopen_df['Open']) / closeopen_df['Open']

    return closeopen_df_rwd, intra_dfs_filled, date_filter

def filter_dates(
        closeopen_df,
        intra_dfs,
        date_filter
):
    # index reworking to dt
    for intra_df in intra_dfs.values(): intra_df.index = pd.to_datetime(intra_df.index, format='mixed')
    for daily_df in closeopen_df.values(): daily_df.index = pd.to_datetime(daily_df.index, format='mixed')
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
        set([date.date() for date in list(intra_dfs_rwd.values())[0].index.to_list()])
    )

    # we add a previous BD to our analysis exple: intra 26/08 needs 25/08
    intra_date_range.sort()
    intra_date_range.append(yesterday(intra_date_range[0]))

    # restriction
    closeopen_dfs_rwd = {}
    for udl, daily_df in closeopen_df.items():
        daily_df.index = daily_df.index.map(lambda x: x.date())
        daily_df = daily_df.loc[daily_df.index.isin(intra_date_range)]
        closeopen_dfs_rwd[udl] = daily_df

    return closeopen_dfs_rwd, intra_dfs_rwd

if __name__=='__main__':
    run_study()