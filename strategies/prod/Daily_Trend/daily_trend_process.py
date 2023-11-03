import time

from processes.quotes_processes import feed_daily_quotes_db, feed_intraday_quotes_db
from processes.positions_processes import load_positions
from strategies.prod.Daily_Trend.daily_trend import run_strat
from tools.bookingbot.new_order import book

"""
Add logs
Add timer
"""


def main():
    # Refresh prices
    feed_intraday_quotes_db(["UCO", "SCO", "^BCBCLI", "CL=F"])
    feed_daily_quotes_db(["UCO", "SCO", "^BCBCLI", "CL=F"])

    # Check position
    pos_dict = load_positions()

    # Check if signal
    signal = run_strat(pos_dict)

    # Decides if invest
    if signal:
        # Checks available cash & deduct qty
        cash_available = 3000
        # signal['Quantity'] = cash_available / signal['Price']
        signal['Quantity'] = 1

    signal = {
        'security_id': 'SCO',
        'way': 'sell',
        'order_type': 'market',
        'quantity': 1,
        'stop_price': 40,
        'limit_price': 40,
    }
    # Books
    book(
        signal
    )

    # Checks execution
    time.sleep(30)
    not_executed = True
    while not_executed:
        new_pos_dict = load_positions()
        if new_pos_dict != pos_dict:
            not_executed = False

    print('')


if __name__ == '__main__':
    main()
