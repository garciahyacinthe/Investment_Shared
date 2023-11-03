import concurrent.futures as cf
from processes.quotes_processes import feed_daily_quotes_db, feed_intraday_quotes_db


def processes_script(tickers_list):
    """
    Script of the strategy
    """
    feed_daily_quotes_db(["UCO", "SCO"])
    feed_intraday_quotes_db(["UCO", "SCO"])




if __name__== '__main__':
    processes_script(["UCO", "SCO"])
    feed_daily_quotes_db(["UCO", "SCO"])


