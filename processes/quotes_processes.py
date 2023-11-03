import concurrent.futures as cf
from tools.market_data.get_quotes import Quotes

def load_customized_quotes():
    print('')

def load_histo_quotes():
    print('')

def feed_daily_quotes_db(tickers):
    """
    Multithreaded
    :param ticker:
    :return:
    """

    results = {}
    with cf.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(
                Quotes,
                ticker=ticker,
                date_range=[],
                quote_type='daily',
                to_print=True
            )
            for ticker in tickers
        }

    for future in cf.as_completed(futures):
        print(future.result())

def feed_intraday_quotes_db(tickers):
    """
    Multithreaded
    :param ticker:
    :return:
    """

    results = {}
    with cf.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(
                Quotes,
                ticker=ticker,
                date_range=[],
                quote_type='intra_2m',
                to_print=True
            )
            for ticker in tickers
        }

    for future in cf.as_completed(futures):
        print(future.result())
        # results.update({futures[future]: future.result()})

    print('')

if __name__== '__main__':
    feed_intraday_quotes_db(["UCO", "SCO", 'USO', 'USL', "^BCBCLI", "CL=F"])
    feed_daily_quotes_db(["UCO", "SCO",'USO', 'USL', "^BCBCLI", "CL=F"])
    # load_histo_quotes()

