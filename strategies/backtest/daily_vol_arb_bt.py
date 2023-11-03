import pandas as pd
import datetime as dt
from strategies.uat.daily_vol_arb import compute_daily_vol_arb_strat_simulation
from databases.paths import BacktestResultsPath


def generate_sample(ticker):

    list_res = []

    # dates
    today = dt.datetime.today()
    # _yesterday = yesterday(today)
    # 5 last Bdays
    date_r = '1BD'
    dates = [date.date() for date in pd.bdate_range(end=dt.datetime.today(), periods=1)]

    # 5 last Bdays
    # date_r = '5BD'
    # dates = [date.date() for date in pd.bdate_range(end=dt.datetime.today(), periods=5)]
    # 10 last Bdays
    # date_r = '10BD'
    # dates = [date.date() for date in pd.bdate_range(end=dt.datetime.today(), periods=10)]
    # 20 last Bdays
    # date_r = '20BD'
    # dates = [date.date() for date in pd.bdate_range(start=dt.datetime.today(), periods=20)]

    # indicators tick
    start_vol = 0.01
    step = 0.008
    start_vol = 0.005
    start_step = 0.005
    max_vol = 0.04
    max_step = 0.02

    # multi
    vol_list = [
        start_vol + (start_vol*0.10)*x
        for x in range(50)
        if (start_vol + (start_vol*0.10)*x) <= max_vol
    ]
    step_list = [
        start_step + (start_step * 0.10) * x
        for x in range(50)
        if (start_step + (start_step * 0.10) * x) <= max_step
    ]

    # process type
    process = 'buy_vs_yesterday_sell_vs_buy'
    # process = 'buy_vs_yesterday_sell_vs_yesterday'
    # process = 'buy_vs_yesterday_sell_vs_yesterday_and_degressive'
    quote_to_buy = 'close_yesterday'
    # quote_to_buy = 'open_today'

    #-------------------------------------------------------------
    for vol in vol_list:
        for step in step_list:
            raw_results = compute_daily_vol_arb_strat_simulation(
                ticker,
                {'daily': 'daily', 'intraday': 'intra_2m'},
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
    final_strat_results = analyze_results_strat_lvl(strat_results)

    final_strat_results.to_excel(BacktestResultsPath +
                                 f'analysis_result_{ticker}_{date_r}_{quote_to_buy}_{process}.xlsx')
    # df.to_excel(BacktestResultsPath + f'analysis_result_{ticker}_single_interval_{process}.xlsx')

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
    generate_sample('UCO')
    generate_sample('SCO')