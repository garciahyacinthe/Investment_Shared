import pandas as pd
import datetime as dt
from strategies.uat.daily_vol_arb import compute_daily_vol_arb_strat_simulation
from databases.paths import BacktestResultsPath, QuotesPath
from tools.misc.database_misc import get_from_db
from tools.misc.dates_misc import yesterday
from tools.strategies_toolbox.intra_vs_close import compare_close_open_one_day

"""
This strat is a range arb one. It computes best entry point during last 10 BD, last 2 BD and [OpenToday vs CloseYesterday]
"""

def run_strat():
    results = {}
    # date_range = pd.bdate_range(
    #     end=dt.datetime.today(),
    #     periods=20,
    #     holidays=["2023-09-04"]
    # )
    date_range = pd.bdate_range(
        end=dt.datetime.today(),
        periods=2,
        freq="C",
        holidays=["2023-09-04"]
    )
    for date in date_range:
        _yesterday = yesterday(date.date(), dayoffs=[dt.date(year=2023, month=9, day=4)])
        # print('today ' + str(date.date()) + '.yesterday '+ str(_yesterday.date()))
        params = generate_params('UCO', _yesterday)
        param_pair = apply_logic(params)
        results[date.date()] = run_with_params('UCO', date.date(), param_pair)
        print('Done with ' + str(date.date()) + '. Return is: ' + str(results[date.date()]['return']))
    print(results)

def apply_logic(params_dict):

    entry_point = 0.3 * float(params_dict['five_bd_entry_point']) + 0.7 * float(params_dict['one_bd_entry_point'])
    gain_interval = 0.3 * float(params_dict['five_bd_gain_interval']) + 0.7 * float(params_dict['five_bd_gain_interval'])
    if float(params_dict['range_close_open']) > float(entry_point):
        entry_point = float(params_dict['range_close_open'])

    return [entry_point, gain_interval]

def run_with_params(ticker, date_run, param_pair):
    """
    Generates the 3 necessary variables pairs.
    5 BD entry and interval
    1 BD entry and interval
    Today's open/close range
    :return:
    -
    """
    interval_dict = {'daily': 'daily', 'intraday': 'intra_2m'}

    res_dict = {}
    list_res = []
    # indicators tick
    # start_vol = 0.005
    # start_step = 0.005
    # max_vol = 0.04
    # max_step = 0.015

    # process type
    process = 'buy_vs_yesterday_sell_vs_buy'
    # process = 'buy_vs_yesterday_sell_vs_yesterday'
    # process = 'buy_vs_yesterday_sell_vs_yesterday_and_degressive'
    quote_to_buy = 'close_yesterday'
    # quote_to_buy = 'open_today'

    # dates
    _yesterday = yesterday(date_run)

    # --------------------------------------------------------------------------------------
    # 1 last Bdays
    date_r = '1BD'
    dates = [date.date() for date in pd.bdate_range(end=date_run, periods=1)]

    # multi
    vol_list = [param_pair[0]]
    step_list = [param_pair[1]]

    #-------------------------------------------------------------
    for vol in vol_list:

        for step in step_list:
            raw_results = compute_daily_vol_arb_strat_simulation(
                ticker,
                interval_dict,
                vol,
                step,
                process,
                quote_to_buy,
                date_range=dates
            )

            simulation_results = analyze_results_simulation_lvl(raw_results)
            list_res.append(simulation_results)
        print(f'Results computed for volat {vol}')

    # aggregation of each interval simulations
    strat_results = pd.concat(list_res)

    # analysis at highest level
    final_strat_results_1BD = analyze_results_strat_lvl(strat_results)

    final_strat_results_1BD.to_excel(BacktestResultsPath +
                                 f'analysis_result_{ticker}_{date_r}_{quote_to_buy}_{process}.xlsx')

    res_dict['one_bd_entry_point'] = final_strat_results_1BD['daily_vol_max_return'].unique()[0]
    res_dict['one_bd_gain_interval'] = final_strat_results_1BD['gain_interval_max_return'].unique()[0]
    res_dict['return'] = final_strat_results_1BD['max_return'].unique()[0]

    # daily_df = get_from_db(
    #     path=QuotesPath + ticker + f'\\{interval_dict["daily"]}_{ticker}.csv',
    #     index_name='timestamp'
    # )
    # intraday_df = get_from_db(
    #     path=QuotesPath + ticker + f'\\{interval_dict["intraday"]}_{ticker}.csv',
    #     index_name='timestamp'
    # )
    #
    # res_dict['range_close_open'] = compare_close_open(daily_df, intraday_df, _yesterday, date_run)

    return res_dict

def generate_params(ticker, date_run):
    """
    Generates the 3 necessary variables pairs.
    5 BD entry and interval
    1 BD entry and interval
    Today's open/close range
    :return:
    -
    """
    interval_dict = {'daily': 'daily', 'intraday': 'intra_2m'}

    res_dict = {}
    list_res = []
    # indicators tick
    start_vol = 0.005
    start_step = 0.005
    max_vol = 0.04
    max_step = 0.015

    # process type
    process = 'buy_vs_yesterday_sell_vs_buy'
    # process = 'buy_vs_yesterday_sell_vs_yesterday'
    # process = 'buy_vs_yesterday_sell_vs_yesterday_and_degressive'
    quote_to_buy = 'close_yesterday'
    # quote_to_buy = 'open_today'

    # dates
    _yesterday = yesterday(date_run)

    # --------------------------------------------------------------------------------------
    # 1 last Bdays
    date_r = '1BD'
    dates = [date.date() for date in pd.bdate_range(end=date_run, periods=1)]

    # multi
    vol_list = [
        start_vol + (start_vol*0.10)*x
        for x in range(20)
        if (start_vol + (start_vol*0.10)*x) <= max_vol
    ]
    step_list = [
        start_step + (start_step * 0.10) * x
        for x in range(10)
        if (start_step + (start_step * 0.10) * x) <= max_step
    ]

    #-------------------------------------------------------------
    for vol in vol_list:
        for step in step_list:
            raw_results = compute_daily_vol_arb_strat_simulation(
                ticker,
                interval_dict,
                vol,
                step,
                process,
                quote_to_buy,
                date_range=dates
            )

            simulation_results = analyze_results_simulation_lvl(raw_results)
            list_res.append(simulation_results)
        print(f'Results computed for volat {vol}')

    # aggregation of each interval simulations
    strat_results = pd.concat(list_res)

    # analysis at highest level
    final_strat_results_1BD = analyze_results_strat_lvl(strat_results)

    final_strat_results_1BD.to_excel(BacktestResultsPath +
                                 f'analysis_result_{ticker}_{date_r}_{quote_to_buy}_{process}.xlsx')
    # df.to_excel(BacktestResultsPath + f'analysis_result_{ticker}_single_interval_{process}.xlsx')

    # --------------------------------------------------------------------------------------
    # 5 last Bdays
    date_r = '5BD'
    dates = [date.date() for date in pd.bdate_range(end=date_run, periods=5)]

    # -------------------------------------------------------------
    for vol in vol_list:
        for step in step_list:
            raw_results = compute_daily_vol_arb_strat_simulation(
                ticker,
                interval_dict,
                vol,
                step,
                process,
                quote_to_buy,
                date_range=dates
            )

            simulation_results = analyze_results_simulation_lvl(raw_results)
            list_res.append(simulation_results)
            print(f'Results computed for volat {vol} and step {step}.')

    # aggregation of each interval simulations
    strat_results = pd.concat(list_res)

    # analysis at highest level
    final_strat_results_5BD = analyze_results_strat_lvl(strat_results)

    final_strat_results_5BD.to_excel(BacktestResultsPath +
                                 f'analysis_result_{ticker}_{date_r}_{quote_to_buy}_{process}.xlsx')
    # df.to_excel(BacktestResultsPath + f'analysis_result_{ticker}_single_interval_{process}.xlsx')

    res_dict['five_bd_entry_point'] = final_strat_results_5BD['daily_vol_max_return'].unique()[0]
    res_dict['five_bd_gain_interval'] = final_strat_results_5BD['gain_interval_max_return'].unique()[0]
    res_dict['one_bd_entry_point'] = final_strat_results_1BD['daily_vol_max_return'].unique()[0]
    res_dict['one_bd_gain_interval'] = final_strat_results_1BD['gain_interval_max_return'].unique()[0]

    daily_df = get_from_db(
        path=QuotesPath + ticker + f'\\{interval_dict["daily"]}_{ticker}.csv',
        index_name='timestamp'
    )
    intraday_df = get_from_db(
        path=QuotesPath + ticker + f'\\{interval_dict["intraday"]}_{ticker}.csv',
        index_name='timestamp'
    )

    res_dict['range_close_open'] = compare_close_open_one_day(daily_df, intraday_df, _yesterday, date_run)

    return res_dict


def analyze_results_simulation_lvl(res_simu):

    macro_results = {}

    # Results gathering
    macro_results['daily_return'] = sum(res_simu.set_index('date')['daily_return'].unique().tolist())
    macro_results['daily_vol'] = res_simu['daily_vol'].unique()[0]
    macro_results['gain_interval'] = res_simu['gain_interval'].unique()[0]
    macro_results['colle'] = sum([res_simu.set_index('date')['colle'].to_dict().values()][0])
    daily_transaction_number_list = [res_simu.set_index('date')['transaction_number'].to_dict().values()][0]
    macro_results['total_transaction_number'] = sum(daily_transaction_number_list)
    macro_results['average_transaction_number'] =\
    sum(daily_transaction_number_list)/len(daily_transaction_number_list)

    macro_results_df = pd.DataFrame.from_dict(macro_results, orient='index').T
    # macro_results_df.to_csv(f'macro_result_{daily_vol}_{gain_interval}.csv')

    return macro_results_df

def analyze_results_strat_lvl(res_strat):

    # max return analysis
    res_strat['max_return'] = max(res_strat['daily_return'])

    res_strat['daily_vol_max_return'] = res_strat.loc[
        res_strat['daily_return'] == max(res_strat['daily_return']), 'daily_vol'
    ].unique()[0]
    res_strat['gain_interval_max_return'] = res_strat.loc[
        res_strat['daily_return'] == max(res_strat['daily_return']), 'gain_interval'
    ].unique()[0]

    # min return analysis
    res_strat['min_return'] = min(res_strat['daily_return'])
    res_strat['daily_vol_min_return'] = res_strat.loc[
        res_strat['daily_return'] == min(res_strat['daily_return']), 'daily_vol'
    ].unique()[0]
    res_strat['gain_interval_min_return'] = res_strat.loc[
        res_strat['daily_return'] == min(res_strat['daily_return']), 'gain_interval'
    ].unique()[0]

    # # ratios
    # res_strat['ratio_colle_per_transaction'] = macro_results['colle']
    # res_strat['min_return']
    return res_strat

if __name__=='__main__':
    run_strat()