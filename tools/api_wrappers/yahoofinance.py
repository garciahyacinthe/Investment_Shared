import yfinance as yf
from tools.misc.objects_helper import partial_flat
from tools.classes.quote import Quote

def get_security_infos_by_ticker(ticker):

    try:
        yf.Ticker(ticker)
        return partial_flat(obj=yf.Ticker(ticker), subobj='info')
    except:
        return {}

def get_intraday_quotes(ticker, interval):
    ticker_basic_data = yf.Ticker(ticker)
    quotes = Quote(
        app_object=ticker_basic_data.history(interval=interval),
        app_name='YahooFinance',
        infos={'ticker': ticker, 'interval': interval}
    )
    return quotes.reworked_df

def get_daily_quotes(ticker, interval):
    ticker_basic_data = yf.Ticker(ticker)
    quotes = Quote(
        app_object=ticker_basic_data.history(interval=interval, period='max'),
        app_name='YahooFinance',
        infos={'ticker': ticker, 'interval': interval}
    )
    return quotes.reworked_df

if __name__=='__main__':

    sec = get_security_infos_by_ticker('CL=F')
    print('')



