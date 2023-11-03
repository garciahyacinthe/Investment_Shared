import pandas as pd
from databases.paths import QuotesPath, StrategiesPath
from tools.misc.database_misc import get_from_db, generate_folder, refresh_db
from tools.strategies_toolbox.intra_vs_close import compare_close_intra

pd.options.mode.chained_assignment = None

def compute_daily_vol_arb_strat(
        ticker_name,
        interval_comparison_dict,
        vol,
        vol_step,
        process_name,
        use_open_or_close
):

    strategy_name = 'daily_vol_arb_simulation'

    daily_df = get_from_db(
        path=QuotesPath + ticker_name + f'\\{interval_comparison_dict["daily"]}_{ticker_name}.csv',
        index_name='timestamp'
    )
    intraday_df = get_from_db(
        path=QuotesPath + ticker_name + f'\\{interval_comparison_dict["intraday"]}_{ticker_name}.csv',
        index_name='timestamp'
    )
    # generates db for this strategy
    generate_folder(StrategiesPath + f'\\{strategy_name}\\{ticker_name}')

    intra_returns = compare_close_intra(close_df=daily_df, intra_df=intraday_df, quote_timing=use_open_or_close)
    # refresh_db(
    #     df=intra_returns,
    #     path=StrategiesPath + f'\\{strategy_name}\\{ticker_name}' + '\\intra_returns.csv'
    # )

    strat_results = compute_returns(vol, vol_step, intra_returns, process_name)

def compute_daily_vol_arb_strat_simulation(
        ticker_name,
        interval_comparison_dict,
        vol,
        vol_step,
        process_name,
        use_open_or_close,
        date_range=[]
):

    strategy_name = 'daily_vol_arb_simulation'

    daily_df = get_from_db(
        path=QuotesPath + ticker_name + f'\\{interval_comparison_dict["daily"]}_{ticker_name}.csv',
        index_name='timestamp'
    )
    intraday_df = get_from_db(
        path=QuotesPath + ticker_name + f'\\{interval_comparison_dict["intraday"]}_{ticker_name}.csv',
        index_name='timestamp'
    )
    # generates db for this strategy
    generate_folder(StrategiesPath + f'\\{strategy_name}\\{ticker_name}')

    intra_returns = compare_close_intra(
        close_df=daily_df,
        intra_df=intraday_df,
        quote_timing=use_open_or_close,
        date_range=date_range
    )
    # refresh_db(
    #     df=intra_returns,
    #     path=StrategiesPath + f'\\{strategy_name}\\{ticker_name}' + '\\intra_returns.csv'
    # )

    strat_results = compute_returns(vol, vol_step, intra_returns, process_name)

    return strat_results

def compute_returns(daily_vol, gain_interval, intra_returns, buy_sell_process_name):

    results = []

    # set_up
    intra_returns['daily_vol'] = daily_vol
    intra_returns['gain_interval'] = gain_interval
    intra_returns['position'] = 0
    intra_returns['order_price'] = 0
    intra_returns['daily_return'] = 0
    intra_returns['colle'] = 0
    intra_returns['transaction_number'] = 0

    # buy and sell process choice
    buy_sell_process = {
        'buy_vs_yesterday_sell_vs_yesterday': buy_sell_process_vs_yesterday,
        'buy_vs_yesterday_sell_vs_buy': buy_sell_process_vs_yesterday_buylevel,
        'buy_vs_yesterday_sell_vs_yesterday_and_degressive': buy_sell_process_vs_yesterday_degressive
    }

    # computing per day
    for day in intra_returns['date'].unique().tolist():

        intraday = intra_returns.loc[
            intra_returns['date'] == day
        ]
        intraday.reset_index(inplace=True)
        # buy/sell process launching though dict
        intraday_df = buy_sell_process[buy_sell_process_name](intraday)
        intraday_df.set_index('timestamp', inplace=True)
        results.append(intraday_df)

    # days concatenation
    results_df = pd.concat(results)
    return results_df

def buy_sell_process_vs_yesterday(df):
    """
    Buy and sell intervals are computed vs close or open yesterday
    :param df:
    :return:
    """
    # indicators
    position = 0
    buy_p = 0
    sell_p = 0
    colle = 0
    transaction_number= 0

    # scroll through minutes, starting with second constatation
    for i in range(len(df))[1:]:

        # go long
        if df.loc[i, 'return'] <= -df.loc[i, 'daily_vol'] \
                and position == 0 \
                and colle == 0:
            df.loc[i, 'order_price'] = df.loc[i, 'Close']
            df.loc[i, 'position'] = 1
            buy_p = df.loc[i, 'Close']
            position += 1
            transaction_number += 1
        # go short
        if df.loc[i, 'return'] >= -df.loc[i, 'daily_vol'] + df.loc[i, 'gain_interval'] \
                and position == 1\
                and colle == 0:
            df.loc[i, 'order_price'] = df.loc[i, 'Close']
            df.loc[i, 'position'] = -1
            sell_p = df.loc[i, 'Close']
            position -= 1
        # go short at close
        if position == 1 \
                and df.loc[i, 'timestamp'].hour == 15 \
                and df.loc[i, 'timestamp'].minute >= 30 \
                and colle == 0:
            df.loc[i, 'order_price'] = df.loc[i, 'Close']
            df.loc[i, 'position'] = -1
            colle = 1
            sell_p = df.loc[i, 'Close']
            position -= 1

    if sell_p != 0:
        df['daily_return'] = (sell_p - buy_p) / buy_p
        df['colle'] = colle
        df['transaction_number'] = transaction_number

    return df

def buy_sell_process_vs_yesterday_buylevel(df):
    """
    Buy vs close/open yesterday, sell vs buy level
    """
    # indicators
    position = 0
    buy_p = 0
    sell_p = 0
    colle = 0
    transaction_number = 0
    return_level_of_entry = 0

    # scroll through minutes, starting with second constatation
    for i in range(len(df))[1:]:

        # go long
        if df.loc[i, 'return'] <= -df.loc[i, 'daily_vol'] \
                and position == 0 \
                and colle == 0:
            df.loc[i, 'order_price'] = df.loc[i, 'Close']
            df.loc[i, 'position'] = 1
            buy_p = df.loc[i, 'Close']
            position += 1
            transaction_number += 1
            return_level_of_entry = df.loc[i, 'return']

        # go short vs return of entry + interval
        if df.loc[i, 'return'] >= return_level_of_entry + df.loc[i, 'gain_interval'] \
                and position == 1\
                and colle == 0:
            df.loc[i, 'order_price'] = df.loc[i, 'Close']
            df.loc[i, 'position'] = -1
            sell_p = df.loc[i, 'Close']
            position -= 1
        # go short at close
        if position == 1 \
                and df.loc[i, 'timestamp'].hour == 15 \
                and df.loc[i, 'timestamp'].minute >= 30 \
                and colle == 0:
            df.loc[i, 'order_price'] = df.loc[i, 'Close']
            df.loc[i, 'position'] = -1
            colle = 1
            sell_p = df.loc[i, 'Close']
            position -= 1

    if sell_p != 0:
        df['daily_return'] = (sell_p - buy_p) / buy_p
        df['colle'] = colle
        df['transaction_number'] = transaction_number

    return df

def buy_sell_process_vs_yesterday_degressive(df):
    """
    Buy and sell intervals are computed vs close or open yesterday
    :param df:
    :return:
    """
    # indicators
    position = 0
    buy_p = 0
    sell_p = 0
    colle = 0
    transaction_number= 0

    # scroll through minutes, starting with second constatation
    for i in range(len(df))[1:]:

        # go long
        if df.loc[i, 'return'] <= -df.loc[i, 'daily_vol'] \
                and position == 0 \
                and colle == 0:
            df.loc[i, 'order_price'] = df.loc[i, 'Close']
            df.loc[i, 'position'] = 1
            buy_p = df.loc[i, 'Close']
            position += 1
            transaction_number += 1
            buy_time = df.loc[i, 'timestamp']

        # go short
        if position == 1:
            if df.loc[i, 'return'] >= -df.loc[i, 'daily_vol'] + degressive_gain_interval(
                    df.loc[i, 'gain_interval'], df.loc[i, 'timestamp'], buy_time) \
                    and position == 1\
                    and colle == 0:
                df.loc[i, 'order_price'] = df.loc[i, 'Close']
                df.loc[i, 'position'] = -1
                sell_p = df.loc[i, 'Close']
                degress_gain_interval = degressive_gain_interval( df.loc[i, 'gain_interval'], df.loc[i, 'timestamp'], buy_time)
                position -= 1
        # go short at close
        if position == 1 \
                and df.loc[i, 'timestamp'].hour == 15 \
                and df.loc[i, 'timestamp'].minute >= 30 \
                and colle == 0:
            df.loc[i, 'order_price'] = df.loc[i, 'Close']
            df.loc[i, 'position'] = -1
            colle = 1
            sell_p = df.loc[i, 'Close']
            position -= 1

    if sell_p != 0:
        df['daily_return'] = (sell_p - buy_p) / buy_p
        df['colle'] = colle
        df['transaction_number'] = transaction_number

    return df

def degressive_gain_interval(gain_interval, time_now, time_buy):
    """
    Multiplies gain interval by a decreasing ratio of
    (number of minutes til closing now / number of minutes til closing from buy)
    It's a variant of the famous time decay
    Why ? Reducing the colles ie stabilize profits. Waiting for the close to clear a colle increase incertainty.
    Result => reduce colle for sure but reduce potential gain and thus whole perf is decreasing

    """
    # close considered @15:50 to allow settlement
    minutes_til_close_from_buy = (15 * 60 + 50) - (time_buy.hour * 60 + time_buy.minute)
    minutes_til_close_from_now = (15 * 60 + 50) - (time_now.hour * 60 + time_now.minute)

    degressive_gain_interval = (minutes_til_close_from_now / minutes_til_close_from_buy ) * gain_interval

    return degressive_gain_interval

if __name__=='__main__':
    # generate_sample()
    # mono udl
    single_result = compute_daily_vol_arb_strat_simulation(
        'SCO',
        {'daily': 'daily', 'intraday': 'intra_2m'},
        0.031773582,
        # 0.020128203,
        0.005,
        'buy_vs_yesterday_sell_vs_yesterday',
        'close_yesterday'
    )
    single_result.to_csv('single_res_SCO_small_interval.csv')
    single_result = compute_daily_vol_arb_strat_simulation(
        'UCO',
        {'daily': 'daily', 'intraday': 'intra_2m'},
        0.024434452,
        # 0.02398797,
        0.005,
        'buy_vs_yesterday_sell_vs_yesterday',
        'close_yesterday'
    )
    single_result.to_csv('single_res_UCO_small_interval.csv')
