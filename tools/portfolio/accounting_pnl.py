from processes.cash_account_processes import load_cash_account
from processes.order_book_processes import load_order_book
from processes.positions_processes import load_positions
from databases.paths import PnLPath
from tools.classes.pnl import PnL

class AccountingPnL(PnL):

    def __init__(self):

        # refreshes both OB and cash account
        load_cash_account()
        load_order_book()
        load_positions()
        self.__init__ = PnL()
        self.db_path = PnLPath

    def print(self):
        self.accounting_pnl.to_csv(self.db_path)