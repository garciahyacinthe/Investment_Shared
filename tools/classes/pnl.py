from tools.misc.classes_misc import iterable
from databases.paths import OrderBookPath, CashAccountPath, PositionsPath
from tools.misc.database_misc import get_from_db
from tools.market_data.get_quotes import load_quotes
import pandas as pd
import datetime as dt

@iterable
class PnL:
    """
    Generic object gathering all details needed to compute the different pnl analyses
    """
    def __init__(self):
        #Load cash account for fees, compute positions, load OB for new deals, load quotes
        self.as_of = dt.datetime.today()
        self.as_of_TminusOne = self.as_of - dt.timedelta(3 if self.as_of.weekday() == 0 else 1)
        self.orders = get_from_db(OrderBookPath,'unique_indicator')
        self.cash_acc = get_from_db(CashAccountPath, 'unique_indicator')
        self.positions = get_from_db(PositionsPath, 'security_id')
        self.spot = load_quotes(self.as_of)
        self.spotTminusOne = load_quotes(self.as_of)


#         self.daily = compute_rolling_pnl(self.orders)
#         self.weekly_roll = compute_rolling_pnl(self.orders)
#         self.monthly_roll = compute_rolling_pnl(self.orders)
#         self.MTD = compute_todate_pnl(self.orders)
#         self.YTD = compute_todate_pnl(self.orders)
#         self.since_inception = compute_todate_pnl(self.orders)
#         self.fees = compute_fees()
#         self.YTD_wfees =
#         self.since_inception_wfees
        print('')
#     def refresh()

