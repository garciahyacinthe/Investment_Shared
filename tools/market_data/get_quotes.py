import pandas as pd
from tools.api_wrappers.wealthsimple import WealthSimple
from tools.api_wrappers.yahoofinance import get_intraday_quotes, get_daily_quotes
from tools.misc.classes_misc import iterable
from tools.misc.database_misc import generate_folder, get_from_db, merge_new_and_old_db, refresh_db, check_if_db
from databases.paths import OrderBookPath, QuotesPath
from databases.mappings import yf_quotes_type_vs_interval

@iterable
class Quotes:

    def __init__(
            self,
            ticker,
            date_range,
            quote_type,
            to_print=True
    ):

        # TODO comparison closing and intraday
        # ws_quotes = get_quotes_from_ws(ticker)
        yf_intra_quotes = get_quotes_from_yf(ticker, quote_type, date_range)

        if to_print is True:
            print_quotes(
                new_db=yf_intra_quotes,
                path_name=QuotesPath,
                ticker_name=ticker,
                file_name=quote_type
            )

def get_quotes_from_ws(ticker):
    #TODO transco sec id to ticker
        ws = WealthSimple()
        quotes_ws = [
            ws.get_quotes_ws(sec_id=sec_id)
            for sec_id in pd.read_csv(OrderBookPath)['security_id'].unique().tolist()
        ]
        return quotes_ws

def get_quotes_from_yf(ticker, type_req, date_r=None):
    get_mapping = {
        'daily': get_daily_quotes,
        'intra_1m': get_intraday_quotes,
        'intra_2m': get_intraday_quotes
    }
    return get_mapping[type_req](ticker, yf_quotes_type_vs_interval[type_req])

def print_quotes(new_db, path_name, ticker_name, file_name):
    # check if folder exists, creates it if none
    generate_folder(path_name + f'\\{ticker_name}')

    # loads df and merges with new one
    if check_if_db(path_name + ticker_name + f'\\{file_name}_{ticker_name}.csv'):
        old_db = get_from_db(path_name + ticker_name + f'\\{file_name}_{ticker_name}.csv', index_name='timestamp')
        new_db = merge_new_and_old_db(new_df=new_db, old_df=old_db, index_name='timestamp')

    # saves to csv
    refresh_db(df=new_db, path=path_name + ticker_name + f'\\{file_name}_{ticker_name}.csv')

    print('Refreshed db: ' + path_name + ticker_name + f'\\{file_name}_{ticker_name}.csv')

if __name__=='__main__':
    Quotes()